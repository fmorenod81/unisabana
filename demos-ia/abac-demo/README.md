# ABAC Demo — Attribute-Based Access Control on AWS

## What is ABAC?

**ABAC (Attribute-Based Access Control)** is an authorization strategy that defines permissions based on **tags** (attributes) attached to:

- **Principals** (IAM users / roles)
- **Resources** (S3 buckets, EC2 instances, etc.)

Instead of writing one policy per user or per resource, you write **one policy** and let AWS evaluate the tags at runtime.

---

## Demo Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Single ABAC Policy                   │
│   Allow s3:* WHERE s3:ResourceTag/team ==               │
│                    aws:PrincipalTag/team                 │
└────────────┬────────────────────────┬───────────────────┘
             │                        │
     ┌───────▼──────┐        ┌────────▼─────┐
     │  alice        │        │  bob          │
     │  tag:         │        │  tag:         │
     │  team=alpha   │        │  team=beta    │
     └───────┬───────┘        └────────┬──────┘
             │                         │
     ✅ ALLOW │                ✅ ALLOW │
             ▼                         ▼
     ┌───────────────┐        ┌────────────────┐
     │  BucketAlpha  │        │  BucketBeta    │
     │  tag:         │        │  tag:          │
     │  team=alpha   │        │  team=beta     │
     └───────────────┘        └────────────────┘
             ▲                         ▲
     ❌ DENY  │                ❌ DENY  │
             │                         │
           bob                       alice
```

---

## Resources Created

| Resource | Type | Tag |
|---|---|---|
| `alice` | IAM User | `team=alpha` |
| `bob` | IAM User | `team=beta` |
| `BucketAlpha` | S3 Bucket | `team=alpha` |
| `BucketBeta` | S3 Bucket | `team=beta` |
| `abac-s3-team-policy` | IAM Managed Policy | — |

---

## The Key Policy (ABAC magic)

```yaml
Condition:
  StringEquals:
    s3:ResourceTag/team: "${aws:PrincipalTag/team}"
```

- `aws:PrincipalTag/team` → reads the **user's** tag at request time
- `s3:ResourceTag/team` → reads the **bucket's** tag at request time
- If they match → **ALLOW**; if not → **DENY**

No hardcoded ARNs. No per-user policies. One policy scales to N users.

---

## Deploy

```bash
aws cloudformation deploy \
  --template-file abac-demo.yaml \
  --stack-name abac-demo \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides AlicePassword=Alice@12345! BobPassword=Bob@12345!
```

## Verify (CLI)

```bash
# Get bucket names from stack outputs
BUCKET_ALPHA=$(aws cloudformation describe-stacks \
  --stack-name abac-demo \
  --query "Stacks[0].Outputs[?OutputKey=='BucketAlphaName'].OutputValue" \
  --output text)

BUCKET_BETA=$(aws cloudformation describe-stacks \
  --stack-name abac-demo \
  --query "Stacks[0].Outputs[?OutputKey=='BucketBetaName'].OutputValue" \
  --output text)

# Upload a test file as alice → should SUCCEED on alpha, FAIL on beta
aws s3 cp test.txt s3://$BUCKET_ALPHA/ --profile alice   # ✅ allowed
aws s3 cp test.txt s3://$BUCKET_BETA/  --profile alice   # ❌ denied

# Upload a test file as bob → should SUCCEED on beta, FAIL on alpha
aws s3 cp test.txt s3://$BUCKET_BETA/  --profile bob     # ✅ allowed
aws s3 cp test.txt s3://$BUCKET_ALPHA/ --profile bob     # ❌ denied
```

## Teardown

```bash
aws cloudformation delete-stack --stack-name abac-demo
```

---

## Key Takeaway

> ABAC lets you write **fewer, more scalable policies**.  
> Adding a new team only requires creating a user with the right tag — no policy changes needed.
