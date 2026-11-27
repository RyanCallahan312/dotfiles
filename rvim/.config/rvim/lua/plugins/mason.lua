return {
  {
    "mason-org/mason.nvim",
    opts = {
      registries = {
        "github:mason-org/mason-registry",
        -- Extra registry for packages that have not landed in mason-org yet.
        "github:Crashdummyy/mason-registry",
      },
    },
  },
}
