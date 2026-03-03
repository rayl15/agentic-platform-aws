########################################################
# AWS Load Balancer Controller
########################################################

resource "helm_release" "aws_load_balancer_controller" {
  name       = "aws-load-balancer-controller"
  repository = "https://aws.github.io/eks-charts"
  chart      = "aws-load-balancer-controller"
  version    = "1.6.2"
  namespace  = "kube-system"

  values = [
    yamlencode({
      clusterName = var.cluster_name

      serviceAccount = {
        create = true
        name   = "aws-load-balancer-controller"
        annotations = var.aws_load_balancer_controller_service_account_role_arn != "" ? {
          "eks.amazonaws.com/role-arn" = var.aws_load_balancer_controller_service_account_role_arn
        } : {}
      }

      region = var.aws_region
      vpcId  = var.vpc_id

      # Enable additional features
      enableServiceMutatorWebhook = false
    })
  ]
}
