# FILE: terraform/main.tf
# MCP Portal: mcp.techhappens.eu
# Three MCP servers (Strategy, Memory, Superretometer) behind single Access policy

terraform {
  required_version = ">= 1.5"
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = ">= 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# ──────────────────────────────────────────────────────────────────
# MCP Servers — registered in AI Controls
# ──────────────────────────────────────────────────────────────────

resource "cloudflare_zero_trust_access_ai_controls_mcp_server" "strategy" {
  account_id = var.cloudflare_account_id
  id         = "strategy"
  name       = "Tech Happens Strategy"
  hostname   = "https://strategy.techhappens.eu/mcp"
  auth_type  = "bearer"

  auth_credentials = jsonencode({
    headers = {
      "CF-Access-Client-Id"     = var.mcp_service_token_client_id
      "CF-Access-Client-Secret" = var.mcp_service_token_client_secret
    }
  })
}

resource "cloudflare_zero_trust_access_ai_controls_mcp_server" "memory" {
  account_id = var.cloudflare_account_id
  id         = "memory"
  name       = "Tech Happens Memory"
  hostname   = "https://memory.techhappens.eu/api/mcp"
  auth_type  = "bearer"

  auth_credentials = jsonencode({
    headers = {
      "CF-Access-Client-Id"     = var.mcp_service_token_client_id
      "CF-Access-Client-Secret" = var.mcp_service_token_client_secret
      "X-Project-ID"            = var.memory_project_id
      "X-API-Key"               = var.memory_api_key
    }
  })
}

resource "cloudflare_zero_trust_access_ai_controls_mcp_server" "superretometer" {
  account_id = var.cloudflare_account_id
  id         = "superretometer"
  name       = "Superretometer"
  hostname   = "https://superretometer.techhappens.eu/mcp"
  auth_type  = "bearer"

  auth_credentials = jsonencode({
    headers = {
      "CF-Access-Client-Id"     = var.mcp_service_token_client_id
      "CF-Access-Client-Secret" = var.mcp_service_token_client_secret
    }
  })
}

# ──────────────────────────────────────────────────────────────────
# MCP Portal — aggregates servers, sets Access policy inline
# ──────────────────────────────────────────────────────────────────

resource "cloudflare_zero_trust_access_ai_controls_mcp_portal" "techhappens" {
  account_id  = var.cloudflare_account_id
  id          = "techhappens-mcp"
  hostname    = "mcp.techhappens.eu"
  name        = "Tech Happens MCP"
  description = "Unified MCP Portal for Tech Happens — Strategy, Memory, Superretometer"
  code_mode     = "off"

  servers = [
    {
      server_id        = cloudflare_zero_trust_access_ai_controls_mcp_server.strategy.id
      default_disabled = false
      on_behalf        = false
    },
    {
      server_id        = cloudflare_zero_trust_access_ai_controls_mcp_server.memory.id
      default_disabled = false
      on_behalf        = false
    },
    {
      server_id        = cloudflare_zero_trust_access_ai_controls_mcp_server.superretometer.id
      default_disabled = false
      on_behalf        = false
    }
  ]
}

# ──────────────────────────────────────────────────────────────────
# Access Application — managed manually via dashboard/API
# (IDP creation requires permissions beyond this token)
# App ID: baf6bbff-5d98-4564-9bf6-877850bf2939
# Policy: *@techhappens.eu via email_domain
# ──────────────────────────────────────────────────────────────────

data "cloudflare_zero_trust_access_application" "mcp_portal" {
  account_id = var.cloudflare_account_id
  app_id     = "baf6bbff-5d98-4564-9bf6-877850bf2939"
}

# ──────────────────────────────────────────────────────────────────
# DNS — CNAME to Cloudflare Gateway (proxied)
# ──────────────────────────────────────────────────────────────────

resource "cloudflare_dns_record" "mcp_portal" {
  zone_id = var.cloudflare_zone_id
  name    = "mcp"
  type    = "CNAME"
  content = "gateway.agents.cloudflare.com"
  ttl     = 1
  proxied = true
}
