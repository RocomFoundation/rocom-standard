# FILE: terraform/variables.tf
# Variables for MCP Portal deployment

variable "cloudflare_api_token" {
  type        = string
  sensitive   = true
  description = "Cloudflare API token with Access + DNS + MCP Portals permissions"
}

variable "cloudflare_account_id" {
  type        = string
  description = "Cloudflare Account ID"
}

variable "cloudflare_zone_id" {
  type        = string
  description = "Cloudflare Zone ID for techhappens.eu"
}

# ── Shared service token (MCP Portal Access App) ──

variable "mcp_service_token_client_id" {
  type        = string
  sensitive   = true
  description = "Service Token Client ID for MCP Portal Access App — shared across all backends"
}

variable "mcp_service_token_client_secret" {
  type        = string
  sensitive   = true
  description = "Service Token Client Secret for MCP Portal Access App"
}

# ── Memory-specific headers ──

variable "memory_project_id" {
  type        = string
  description = "Memory project ID"
  default     = "229d3378-5eda-42ab-9bfa-133f6360cd34"
}

variable "memory_api_key" {
  type        = string
  sensitive   = true
  description = "Memory API key for MCP endpoint"
}
