<script lang="ts">
	import Graph from '$lib/graph.svelte';

	async function getElements() {
		// const res = await fetch(`http://0.0.0.0:8000/data`);
		const res = await fetch(`http://0.0.0.0:8000/oas_data`);
		const elements = await res.json();

		if (res.ok) {
			console.log(elements);
			return elements;
		} else {
			throw new Error(elements);
		}
	}
	let promise = getElements();
</script>

{#await promise}
	<p>...waiting</p>
{:then elements}
	<Graph {elements} />
{:catch error}
	<p style="color: red">{error.message}</p>
{/await}
