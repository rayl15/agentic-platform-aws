########################################################
# Storage Class
########################################################

resource "kubernetes_storage_class_v1" "gp3" {
  metadata {
    name = var.storage_class_name

    annotations = {
      "storageclass.kubernetes.io/is-default-class" = "true"
    }

    labels = {
      "app.kubernetes.io/name"       = "storage-class"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  storage_provisioner    = "ebs.csi.aws.com"
  reclaim_policy         = "Delete"
  volume_binding_mode    = "WaitForFirstConsumer"
  allow_volume_expansion = true

  parameters = {
    type   = "gp3"
    fsType = "ext4"
  }
}
