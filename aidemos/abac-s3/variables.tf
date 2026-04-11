variable "projects" {
  description = "Map of project names to their tag values"
  type        = map(string)
  default = {
    alpha = "alpha"
    beta  = "beta"
  }
}
