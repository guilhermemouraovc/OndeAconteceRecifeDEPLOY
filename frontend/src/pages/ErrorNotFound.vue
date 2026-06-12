<template>
  <q-page class="flex flex-center bg-landing">
    <EmptyState
      title="Página não encontrada"
      message="O endereço que você tentou acessar não existe."
      button-label="Ir para a agenda"
      :button-to="{ name: 'home' }"
      icon="explore_off"
    />
  </q-page>
</template>

<script setup>
import EmptyState from 'components/EmptyState.vue'
</script>
