{{- define "app.name" -}}
{{- .Release.Name }}
{{- end }}

{{- define "app.namespace" -}}
{{- .Release.Namespace }}
{{- end }}

{{- define "app.image" -}}
{{- $config := (lookup "v1" "ConfigMap" .Values.namespace "agentic-platform-config").data -}}
{{- printf "%s.dkr.ecr.%s.amazonaws.com/%s:%s" $config.AWS_ACCOUNT_ID $config.AWS_DEFAULT_REGION .Values.image.repository .Values.image.tag -}}
{{- end }}

{{- define "app.irsaRoleArn" -}}
{{- if .Values.serviceAccount.irsaConfigKey -}}
{{- index (lookup "v1" "ConfigMap" .Values.namespace "agentic-platform-config").data .Values.serviceAccount.irsaConfigKey -}}
{{- end -}}
{{- end }}