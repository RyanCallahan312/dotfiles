local wezterm = require("wezterm")
local config = wezterm.config_builder()

config.color_scheme = "Eldritch"
config.hide_tab_bar_if_only_one_tab = true
config.window_padding = {
	left = 0,
	right = 0,
	top = 0,
	bottom = 0,
}
config.font = wezterm.font("Hack Nerd Font Mono")
config.line_height = 1.26

config.keys = {
	-- Turn off the default CMD-m Hide action, allowing CMD-m to
	-- be potentially recognized and handled by the tab
	{
		key = "Enter",
		mods = "ALT",
		action = wezterm.action.DisableDefaultAssignment,
	},
}
-- config.window_frame = {
--
-- 	-- The font used in the tab bar.
-- 	-- Roboto Bold is the default; this font is bundled
-- 	-- with wezterm.
-- 	-- Whatever font is selected here, it will have the
-- 	-- main font setting appended to it to pick up any
-- 	-- fallback fonts you may have used there.
-- 	font = wezterm.font({ family = "Roboto", weight = "Bold" }),
--
-- 	-- The size of the font in the tab bar.
-- 	-- Default to 10.0 on Windows but 12.0 on other systems
-- 	font_size = 10.5,
--
-- 	-- The overall background color of the tab bar when
-- 	-- the window is focused
-- 	active_titlebar_bg = "#333333",
--
-- 	-- The overall background color of the tab bar when
-- 	-- the window is not focused
-- 	inactive_titlebar_bg = "#333333",
-- }
--
-- config.colors = {
-- 	tab_bar = {
--
-- 		-- The color of the inactive tab bar edge/divider
-- 		inactive_tab_edge = "#575757",
-- 	},
-- }

return config
