import argparse
import json
from decimal import Decimal
import boto3
from botocore.exceptions import BotoCoreError, ClientError


class DecimalEncoder(json.JSONEncoder):
    """Encoder para convertir objetos Decimal de boto3 a tipos serializables en JSON."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def get_autoscaling_info(application_autoscaling_client, resource_id: str):
    """Obtiene información sobre las políticas de autoescalamiento para una tabla o GSI."""
    try:
        response = application_autoscaling_client.describe_scalable_targets(
            ServiceNamespace="dynamodb",
            ResourceIds=[resource_id]
        )
        targets = response.get("ScalableTargets", [])
        scaling_info = {}
        for target in targets:
            dimension = target["ScalableDimension"]
            scaling_info[dimension] = {
                "MinCapacity": target.get("MinCapacity"),
                "MaxCapacity": target.get("MaxCapacity")
            }
        return scaling_info
    except Exception:
        return {}


def format_autoscaling_details(scaling_data, read_dim, write_dim):
    """Formatea la información de autoescalamiento para lectura y escritura."""
    read_info = scaling_data.get(read_dim)
    write_info = scaling_data.get(write_dim)

    read_str = f"Habilitado (Mín: {read_info['MinCapacity']}, Máx: {read_info['MaxCapacity']})" if read_info else "No configurado / Deshabilitado"
    write_str = f"Habilitado (Mín: {write_info['MinCapacity']}, Máx: {write_info['MaxCapacity']})" if write_info else "No configurado / Deshabilitado"

    return read_str, write_str


def describe_detailed_provisioning(dynamodb_client, autoscaling_client, table_name: str) -> None:
    """Muestra la estructura, configuración de aprovisionamiento detallada y rendimiento de la tabla."""
    response = dynamodb_client.describe_table(TableName=table_name)
    table = response["Table"]

    print("==================================================================")
    print(f" INFORMACIÓN DETALLADA Y APROVISIONAMIENTO: {table_name}")
    print("==================================================================")

    # 1. Información General de la Tabla
    table_class_summary = table.get("TableClassSummary", {})
    table_class = table_class_summary.get("TableClass", "STANDARD")
    status = table.get("TableStatus", "N/A")
    item_count = table.get("ItemCount", 0)
    size_bytes = table.get("TableSizeBytes", 0)

    print(f"Estado de la Tabla         : {status}")
    print(f"Clase de Tabla (Storage)   : {table_class}")
    print(f"Conteo de Ítems (Aprox.)   : {item_count:,}")
    print(f"Tamaño de Tabla (Aprox.)   : {size_bytes / (1024 * 1024):.2f} MB ({size_bytes:,} bytes)")

    # 2. Esquema de Claves Primarias
    print("\n--- Esquema de Clave Primaria (Primary Key) ---")
    key_schema = table.get("KeySchema", [])
    attr_definitions = {
        attr["AttributeName"]: attr["AttributeType"]
        for attr in table.get("AttributeDefinitions", [])
    }
    for key in key_schema:
        name = key["AttributeName"]
        ktype = "Partition Key (HASH)" if key["KeyType"] == "HASH" else "Sort Key (RANGE)"
        dtype = attr_definitions.get(name, "Desconocido")
        print(f"  • {ktype:20s}: {name} (Tipo: {dtype})")

    # 3. Billing Mode, Capacidad y Autoescalamiento
    billing_summary = table.get("BillingModeSummary", {})
    billing_mode = billing_summary.get("BillingMode", table.get("BillingMode", "PROVISIONED"))

    print("\n--- Capacidad y Aprovisionamiento de la Tabla ---")
    print(f"Modo de Facturación / Capacidad : {billing_mode}")

    table_resource_id = f"table/{table_name}"
    autoscaling_data = get_autoscaling_info(autoscaling_client, table_resource_id)

    if billing_mode == "PAY_PER_REQUEST":
        ondemand_throughput = table.get("OnDemandThroughput", {})
        max_read = ondemand_throughput.get("MaxReadRequestUnits", "Sin límite explícito (Max AWS Account Limit)")
        max_write = ondemand_throughput.get("MaxWriteRequestUnits", "Sin límite explícito (Max AWS Account Limit)")
        print(f"  • Read Request Units Máximos  : {max_read}")
        print(f"  • Write Request Units Máximos : {max_write}")
    else: # PROVISIONED
        provisioned = table.get("ProvisionedThroughput", {})
        rcu = provisioned.get("ReadCapacityUnits", 0)
        wcu = provisioned.get("WriteCapacityUnits", 0)
        print(f"  • Read Capacity Units (RCU)   : {rcu}")
        print(f"  • Write Capacity Units (WCU)  : {wcu}")

        read_auto, write_auto = format_autoscaling_details(
            autoscaling_data,
            "dynamodb:table:ReadCapacityUnits",
            "dynamodb:table:WriteCapacityUnits"
        )
        print(f"  • Autoescalamiento Lectura   : {read_auto}")
        print(f"  • Autoescalamiento Escritura : {write_auto}")

    # 4. Warm Throughput
    warm_tp = table.get("WarmThroughput", {})
    if warm_tp:
        print("\n--- Warm Throughput (Pre-provisioned Instant Capacity) ---")
        print(f"  • Read Units Regulados (Warm) : {warm_tp.get('ReadUnitsPerSecond', 'N/A')}")
        print(f"  • Write Units Regulados (Warm): {warm_tp.get('WriteUnitsPerSecond', 'N/A')}")
        print(f"  • Estado                      : {warm_tp.get('Status', 'N/A')}")

    # 5. Global Secondary Indexes (GSI)
    gsis = table.get("GlobalSecondaryIndexes", [])
    print(f"\n--- Índices Secundarios Globales (GSI) [{len(gsis)}] ---")
    if not gsis:
        print("  Ninguno registrado.")
    else:
        for gsi in gsis:
            gsi_name = gsi["IndexName"]
            gsi_status = gsi.get("IndexStatus", "N/A")
            gsi_size = gsi.get("IndexSizeBytes", 0)
            gsi_items = gsi.get("ItemCount", 0)

            print(f"\n  [GSI] {gsi_name}")
            print(f"    • Estado                 : {gsi_status}")
            print(f"    • Tamaño / Ítems (Aprox.): {gsi_size / (1024 * 1024):.2f} MB / {gsi_items:,} ítems")

            # Keys
            keys_desc = ", ".join([f"{k['AttributeName']} ({k['KeyType']})" for k in gsi.get("KeySchema", [])])
            print(f"    • Claves                 : {keys_desc}")

            # Capacidad & Autoescalamiento GSI
            if billing_mode == "PAY_PER_REQUEST":
                gsi_ondemand = gsi.get("OnDemandThroughput", {})
                print(f"    • Max Read Units         : {gsi_ondemand.get('MaxReadRequestUnits', 'Default/Unlimited')}")
                print(f"    • Max Write Units        : {gsi_ondemand.get('MaxWriteRequestUnits', 'Default/Unlimited')}")
            else:
                gsi_prov = gsi.get("ProvisionedThroughput", {})
                print(f"    • RCU / WCU              : {gsi_prov.get('ReadCapacityUnits', 0)} RCU / {gsi_prov.get('WriteCapacityUnits', 0)} WCU")

                gsi_resource_id = f"table/{table_name}/index/{gsi_name}"
                gsi_autoscaling = get_autoscaling_info(autoscaling_client, gsi_resource_id)
                r_auto, w_auto = format_autoscaling_details(
                    gsi_autoscaling,
                    "dynamodb:index:ReadCapacityUnits",
                    "dynamodb:index:WriteCapacityUnits"
                )
                print(f"    • Autoescalamiento (R/W) : R: {r_auto} | W: {w_auto}")

            # Warm Throughput GSI
            gsi_warm = gsi.get("WarmThroughput", {})
            if gsi_warm:
                print(f"    • Warm Throughput        : R: {gsi_warm.get('ReadUnitsPerSecond')} / W: {gsi_warm.get('WriteUnitsPerSecond')}")

    # 6. Local Secondary Indexes (LSI)
    lsis = table.get("LocalSecondaryIndexes", [])
    print(f"\n--- Índices Secundarios Locales (LSI) [{len(lsis)}] ---")
    if not lsis:
        print("  Ninguno registrado.")
    else:
        for lsi in lsis:
            lsi_name = lsi["IndexName"]
            lsi_size = lsi.get("IndexSizeBytes", 0)
            lsi_items = lsi.get("ItemCount", 0)
            keys_desc = ", ".join([f"{k['AttributeName']} ({k['KeyType']})" for k in lsi.get("KeySchema", [])])

            print(f"\n  [LSI] {lsi_name}")
            print(f"    • Tamaño / Ítems (Aprox.): {lsi_size / (1024 * 1024):.2f} MB / {lsi_items:,} ítems")
            print(f"    • Claves                 : {keys_desc}")
            print("    • Capacidad              : Utiliza el RCU/WCU aprovisionado de la tabla principal.")


def sample_table_items(dynamodb_resource, table_name: str, limit: int = 5) -> None:
    """Escanea y muestra un número limitado de registros de la tabla."""
    table = dynamodb_resource.Table(table_name)
    response = table.scan(Limit=limit)
    items = response.get("Items", [])

    print("\n==================================================================")
    print(f" MUESTRA DE REGISTROS (MÁXIMO {limit})")
    print("==================================================================")

    if not items:
        print("La tabla no contiene registros.")
        return

    for idx, item in enumerate(items, start=1):
        print(f"\n--- Registro #{idx} ---")
        print(json.dumps(item, indent=2, cls=DecimalEncoder, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="Inspecciona métricas detalladas de aprovisionamiento, esquema y registros de una tabla en DynamoDB."
    )
    parser.add_argument("table_name", type=str, help="Nombre de la tabla de DynamoDB")
    parser.add_argument(
        "--region",
        type=str,
        default="us-east-1",
        help="Región de AWS (por defecto: us-east-1)",
    )

    args = parser.parse_args()

    try:
        dynamodb_client = boto3.client("dynamodb", region_name=args.region)
        dynamodb_resource = boto3.resource("dynamodb", region_name=args.region)
        autoscaling_client = boto3.client("application-autoscaling", region_name=args.region)

        describe_detailed_provisioning(dynamodb_client, autoscaling_client, args.table_name)
        sample_table_items(dynamodb_resource, args.table_name, limit=5)

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ResourceNotFoundException":
            print(f"Error: La tabla o recurso '{args.table_name}' no existe en la región {args.region}.")
        elif error_code == "AccessDeniedException":
            print(f"Error de permisos: Asegúrate de tener permisos para 'dynamodb:DescribeTable' y 'application-autoscaling:DescribeScalableTargets'.")
        else:
            print(f"Error de AWS: {e.response['Error']['Message']}")
    except BotoCoreError as e:
        print(f"Error de configuración o credenciales de boto3: {e}")


if __name__ == "__main__":
    main()