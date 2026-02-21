<script lang="ts">
  import { onMount } from 'svelte';
  
  let name = 'Svelte Template';
  let count = 0;
  let data = [];
  let loading = false;
  let error = '';
  
  async function fetchData() {
    loading = true;
    error = '';
    try {
      const response = await fetch('https://jsonplaceholder.typicode.com/posts');
      if (!response.ok) throw new Error('Network response was not ok');
      data = await response.json();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Unknown error occurred';
    } finally {
      loading = false;
    }
  }

  function increment() {
    count++;
  }

  function decrement() {
    if (count > 0) {
      count--;
    }
  }

  onMount(() => {
    fetchData();
  });
</script>

<main>
  <h1>{name}</h1>
  <p>Welcome to your SvelteKit application</p>
  
  <div class="counter">
    <h2>Counter: {count}</h2>
    <button on:click={increment}>+</button>
    <button on:click={decrement}>-</button>
  </div>
  
  <div class="data-section">
    <h2>Data from API</h2>
    {#if loading}
      <p>Loading...</p>
    {:else if error}
      <p class="error">Error: {error}</p>
    {:else}
      <ul>
        {#each data.slice(0, 5) as item}
          <li>{item.title}</li>
        {/each}
      </ul>
    {/if}
  </div>
  
  <div class="controls">
    <button on:click={fetchData}>Refresh Data</button>
  </div>
</main>

<style>
  main {
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
  }
  
  h1 {
    color: #ff3e00;
    font-size: 2.8em;
    font-weight: 100;
    line-height: 1.2;
    margin: 0;
  }
  
  .counter {
    margin: 2rem 0;
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .counter h2 {
    margin: 0;
  }
  
  .counter button {
    font-size: 1.5rem;
    padding: 0.5rem 1rem;
    border: none;
    background-color: #ff3e00;
    color: white;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .counter button:hover {
    background-color: #c33800;
  }
  
  .data-section {
    margin: 2rem 0;
  }
  
  .data-section h2 {
    margin-bottom: 1rem;
  }
  
  .data-section ul {
    list-style: none;
    padding: 0;
  }
  
  .data-section li {
    padding: 0.5rem 0;
    border-bottom: 1px solid #eee;
  }
  
  .error {
    color: #ff3e00;
  }
  
  .controls {
    margin-top: 2rem;
  }
  
  .controls button {
    background-color: #ff3e00;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .controls button:hover {
    background-color: #c33800;
  }
</style>