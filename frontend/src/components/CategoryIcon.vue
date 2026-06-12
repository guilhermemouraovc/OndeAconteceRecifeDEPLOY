<template>
  <q-icon v-if="typeof icon === 'string'" :name="icon" :class="iconClass" />
</template>

<script setup>
defineProps({
  icon: { type: [Object, String], required: true },
  iconClass: { type: String, default: '' },
})
</script>
