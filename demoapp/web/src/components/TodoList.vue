<template>
  <div>
    <v-snackbar v-model="snackbar" color="error" outlined :timeout="5000" top>
      {{ errorMessage }}
    </v-snackbar>
    <v-row align="center">
      <v-col
        sm="8" offset-sm="2"
        md="6" offset-md="3"
        lg="4" offset-lg="4"
      >
        <v-card outlined :loading="loading">
          <v-card-title>{{ title }}</v-card-title>
          <v-btn block elevation="0" @click="reload">Reload</v-btn>

          <v-form @submit.prevent="add(newTask)">
            <v-container>
              <v-row>
                <v-col cols="8" sm="9">
                  <v-text-field label="New task" v-model="newTask"></v-text-field>
                </v-col>
                <v-col cols="4" sm="3">
                  <div class="mt-4" style="min-width: 76px">
                    <v-btn x-small fab elevation="0" @click="add(newTask)" color="teal" :disabled="!newTask">
                      <v-icon color="white">mdi-check</v-icon>
                    </v-btn>
                    <v-btn x-small fab elevation="0" class="ml-2" @click="newTask=null" :disabled="!newTask">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-form>

          <v-card-text>
            <v-list tow-line>
              <v-subheader>To Do</v-subheader>

              <v-list-item-group>
                <template v-for="item in todoList">
                  <v-list-item :key="item.id">
                    <v-list-item-action>
                      <v-checkbox v-model="item.is_done" @change="toggle(item)"></v-checkbox>
                    </v-list-item-action>

                    <v-list-item-content>
                      <v-list-item-title>{{ item.title }}</v-list-item-title>
                    </v-list-item-content>

                    <v-list-item-action>
                      <v-btn small icon color="warning" @click="remove(item)">
                        <v-icon>mdi-trash-can-outline</v-icon>
                      </v-btn>
                    </v-list-item-action>
                  </v-list-item>
                </template>
              </v-list-item-group>
            </v-list>

            <v-divider></v-divider>

            <v-list>
              <v-subheader>Done</v-subheader>

              <v-list-item-group>
                <template v-for="item in doneList">
                  <v-list-item :key="item.id">
                    <v-list-item-action>
                      <v-checkbox v-model="item.is_done" @change="toggle(item)"></v-checkbox>
                    </v-list-item-action>

                    <v-list-item-content>
                      <v-list-item-title>
                        <span style="text-decoration: line-through">
                          {{ item.title }}
                        </span>
                      </v-list-item-title>
                    </v-list-item-content>

                    <v-list-item-action>
                      <v-btn small icon color="warning" @click="remove(item)">
                        <v-icon>mdi-trash-can-outline</v-icon>
                      </v-btn>
                    </v-list-item-action>
                  </v-list-item>
                </template>
              </v-list-item-group>
            </v-list>
          </v-card-text>

        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import TaskService from '@/services/task'

export default {
  name: 'TodoList',
  props: {
    title: String
  },
  data() {
    return {
      newTask: null,
      allList: [],
      loading: false,
      snackbar: false,
      errorMessage: null
    }
  },
  mounted() {
    this.reload()
  },
  computed: {
    todoList() {
      return this.allList.filter(item => !item.is_done)
    },
    doneList() {
      return this.allList.filter(item => !!item.is_done)
    }
  },
  methods: {
    reload() {
      this.loading = true
      this.errorMessage = null
      TaskService.list()
        .then(resp => this.allList = resp.data)
        .catch(err => {
          this.errorMessage = err
          this.snackbar = true
        })
        .then(() => this.loading = false)
    },

    add(task) {
      if (task) {
        const newId = this.allList.length + 1
        this.loading = true
        this.errorMessage = null
        TaskService.create({title: task})
          .then(resp => {
            this.allList.push(resp.data)
          })
          .catch(err => {
            this.errorMessage = err
            this.snackbar = true
          })
          .then(() => {
            this.newTask = null
            this.reload()
          })
      }
    },

    toggle(item) {
      this.loading = true
      this.errorMessage = null
      TaskService.toggle(item.id, item.is_done)
        .catch(err => {
          this.errorMessage = err
          this.snackbar = true
        })
        .then(() => this.reload())
    },

    remove(item) {
      this.loading = true
      this.errorMessage = null
      TaskService.delete(item.id)
        .catch(err => {
          this.errorMessage = err
          this.snackbar = true
        })
        .then(() => this.reload())
    }
  }
}
</script>

<style lang="scss">

</style>
