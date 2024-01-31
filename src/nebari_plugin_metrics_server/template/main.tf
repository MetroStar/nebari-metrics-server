locals {
  name             = var.name
  create_namespace = var.create_namespace
  namespace        = var.namespace
  overrides        = var.overrides

  affinity = var.affinity != null && lookup(var.affinity, "enabled", false) ? {
    enabled = true
    selector = try(
      { for k in ["default"] : k => length(var.affinity.selector[k]) > 0 ? var.affinity.selector[k] : var.affinity.selector.default },
      {
        default = var.affinity.selector
      },
    )
    } : {
    enabled  = false
    selector = null
  }

  chart_namespace = local.create_namespace ? kubernetes_namespace.this[0].metadata[0].name : local.namespace
}

resource "kubernetes_namespace" "this" {
  count = local.create_namespace ? 1 : 0

  metadata {
    name = local.namespace
  }
}

resource "helm_release" "metrics_server" {
  name      = local.name
  namespace = local.chart_namespace

  repository = "https://kubernetes-sigs.github.io/metrics-server/"
  chart      = "metrics-server"
  version    = "3.11.0"

  values = [
    yamlencode({
      installCRDs = true
      affinity = local.affinity.enabled ? {
        nodeAffinity = {
          requiredDuringSchedulingIgnoredDuringExecution = {
            nodeSelectorTerms = [
              {
                matchExpressions = [
                  {
                    key      = "eks.amazonaws.com/nodegroup"
                    operator = "In"
                    values   = [local.affinity.selector.default]
                  }
                ]
              }
            ]
          }
        }
      } : {}
    }),
    yamlencode(lookup(local.overrides, "metrics-server", {})),
  ]
}