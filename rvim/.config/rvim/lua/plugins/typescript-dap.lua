return {
  {
    "mfussenegger/nvim-dap",
    optional = true,
    dependencies = {
      {
        "mason-org/mason.nvim",
        opts = function(_, opts)
          opts.ensure_installed = opts.ensure_installed or {}
          table.insert(opts.ensure_installed, "js-debug-adapter")
        end,
      },
    },
    opts = function()
      local dap = require("dap")

      -- Prefer Mason's installed adapter, but keep a predictable fallback path.
      local js_debug_adapter_path
      local registry_ok, registry = pcall(require, "mason-registry")
      if registry_ok then
        local ok, pkg = pcall(registry.get_package, "js-debug-adapter")
        if ok and pkg and pkg.get_install_path then
          js_debug_adapter_path = pkg:get_install_path()
        end
      end
      js_debug_adapter_path = js_debug_adapter_path
        or (vim.fn.stdpath("data") .. "/mason/packages/js-debug-adapter")

      -- Expose both Node and Bun entrypoints for the same debug server.
      dap.adapters["pwa-node"] = {
        type = "server",
        host = "localhost",
        port = "${port}",
        executable = {
          command = "node",
          args = {
            js_debug_adapter_path .. "/js-debug/src/dapDebugServer.js",
            "${port}",
          },
        },
      }

      dap.adapters["pwa-bun"] = {
        type = "server",
        host = "localhost",
        port = "${port}",
        executable = {
          command = "bunx",
          args = {
            "--bun",
            js_debug_adapter_path .. "/js-debug/src/dapDebugServer.js",
            "${port}",
          },
        },
      }

      -- Add configuration for Vite + Bun
      dap.configurations.typescript = {
        {
          type = "pwa-node",
          request = "launch",
          name = "Launch Vite App (Bun)",
          cwd = "${workspaceFolder}",
          program = "${workspaceFolder}/node_modules/.bin/vite",
          runtimeExecutable = "bun",
          resolveSourceMapLocations = {
            "${workspaceFolder}/**",
            "!**/node_modules/**",
          },
          skipFiles = { "<node_internals>/**" },
          sourceMaps = true,
        },
        {
          type = "pwa-node",
          request = "attach",
          name = "Attach to Vite App (Bun)",
          cwd = "${workspaceFolder}",
          processId = require("dap.utils").pick_process,
          skipFiles = { "<node_internals>/**" },
          sourceMaps = true,
        },
      }

      -- Reuse the same launch/attach profiles for plain JavaScript projects.
      dap.configurations.javascript = dap.configurations.typescript
    end,
  },
}
