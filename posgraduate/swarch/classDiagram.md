classDiagram
    class AtributoDeCalidad {
        +String nombre
        +String estimulo
        +String respuesta
        +motiva()
    }
    class Tactica {
        +String tecnica
        +String control
        +refina()
    }
    class PatronArquitectonico {
        +String estructura
        +String contexto
        +empaqueta()
    }
    class EstiloArquitectonico {
        +String familia
        +String restricciones
        +define_vocabulario()
    }

    AtributoDeCalidad "1" -- "*" Tactica : es satisfecha por
    Tactica "*" --o "1..*" PatronArquitectonico : es organizada en
    PatronArquitectonico "*" -- "*" EstiloArquitectonico : se adhiere a / conforma
    EstiloArquitectonico "1" -- "*" AtributoDeCalidad : influye/restringe