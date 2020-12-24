<template>
  <v-app>
    <v-app-bar
      app
      color="darkgrey"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Vuetify Logo"
          class="shrink mr-2"
          contain
          src="https://cdn.vuetifyjs.com/images/logos/vuetify-logo-dark.png"
          transition="scale-transition"
          width="40"
        />
        <div style="font-size:28px; font-weight:bold;">
          Simple To-Do List
        </div>
      </div>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <TodoList title="Simple To-Do List" />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import TodoList from './components/TodoList';

export default {
  name: 'App',

  components: {
    TodoList,
  },

  data: () => ({
    //
  }),
};
</script>
