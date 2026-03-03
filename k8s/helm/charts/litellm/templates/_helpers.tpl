{{- define "litellm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "litellm.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "litellm.namespace" -}}
{{- default .Release.Namespace .Values.namespace }}
{{- end }}

{{- define "litellm.image" -}}
{{- printf "%s.dkr.ecr.%s.amazonaws.com/%s:%s" .Values.aws.account .Values.aws.region .Values.image.repository .Values.image.tag -}}
{{- end }}

{{- define "litellm.irsaRoleArn" -}}
{{- (lookup "v1" "ConfigMap" .Values.namespace "agentic-platform-config").data.LITELLM_ROLE_ARN -}}
{{- end }}
