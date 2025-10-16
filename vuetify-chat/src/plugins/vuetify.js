/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";

// Composables
import { createVuetify } from "vuetify";

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: 'banking',
    themes: {
      banking: {
        dark: false,
        colors: {
          // Main brand colors
          background: "#ebecf5", // Light background
          primary: "#1e2633", // Navy - primary actions and text
          secondary: "#516077", // Greyed out text
          
          // Surface colors
          surface: "#ffffff", // White cards
          panel: "#1e2633", // Navy panel/header
          items: "#f4f4f9", // Section card wrapper
          'section-card': "#ffffff", // Section card background
          
          // Interactive elements
          select: "#4a90e2", // Subtle blue accent for selections
          hover: "#e8e9f0", // Subtle hover state
          
          // Scrollbar
          scroll: "#516077", // Greyed out
          track: "#ebecf5", // Background color
          
          // Status and feedback
          success: "#4caf50",
          warning: "#ff9800",
          error: "#f44336",
          info: "#2196F3",
          
          // Text colors
          'text-primary': "#212121", // Main text
          'text-secondary': "#516077", // Greyed out text
          'text-on-navy': "#ffffff", // Text on navy background
          
          // Accent colors (subtle)
          accent: "#4a90e2", // Subtle blue
          'accent-secondary': "#7c9cbf", // Lighter blue
          
          // UI elements
          submenu: "#ffffff",
          appbar: "#1e2633",
          send: "#4a90e2", // Accent blue for send button
          
          // Logo colors
          logoleft: "#1e2633",
          logoright: "#4a90e2",
          
          // Icons
          icons: "#516077",
        },
      },
      midnight: {
        colors: {
          icons: "#78909C",
          secondary: "#FFA000",
          background: "#ECEFF1",
          primary: "#ffffff",
          panel: "#263238",
          items: "#37474f",
          select: "#FFA000",
          scroll: "#BDBDBD",
          track: "#1a1a1a",
          submenu: "#E0E0E0",
          appbar: '#546E7A',
          logoleft: "#263238",
          logoright: "#ffffff",
          send: '#263238',
        },
      },
      teal: {
        colors: {
          background: "#F5F5F5",
          primary: "#009688",
          secondary: "#7986CB",
          icons: "#80CBC4",
          panel: "#B2DFDB",
          items: "#E0F2F1",
          select: "#26A69A",
          scroll: "#009688",
          track: "#b2e6e1",
          submenu:  "#E0F2F1",
          appbar: '#B2DFDB',
          logoleft: "#80CBC4",
          logoright: "#00796B",
          send: "#009688",
        },
      },
    },
  },
});
