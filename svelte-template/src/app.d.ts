import App from "./App.svelte";

const app = new App({
  target: document.getElementById("svelte"),
  props: {
    name: "Svelte Template",
  },
});

export default app;