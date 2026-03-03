########################################################
# External Secrets Operator
########################################################

resource "helm_release" "external_secrets" {
  name             = "external-secrets"
  repository       = "https://charts.external-secrets.io"
  chart            = "external-secrets"
  version          = "0.9.11"
  namespace        = "external-secrets-system"
  create_namespace = true

  values = [
    yamlencode({
      installCRDs = true

      serviceAccount = {
        annotations = var.external_secrets_service_account_role_arn != "" ? {
          "eks.amazonaws.com/role-arn" = var.external_secrets_service_account_role_arn
        } : {}
      }

      securityContext = {
        fsGroup = 65534
      }
    })
  ]
}
