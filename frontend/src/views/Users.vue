<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('nav.users') }}
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="users"
              :loading="loading"
              :search="search"
              class="elevation-1"
            >
              <template v-slot:top>
                <v-text-field
                  v-model="search"
                  :label="$t('common.search')"
                  prepend-inner-icon="mdi-magnify"
                  variant="outlined"
                  hide-details
                  class="mb-4"
                ></v-text-field>
              </template>
              
              <template v-slot:item.role="{ item }">
                <v-chip
                  :color="item.role === 'admin' ? 'error' : 'primary'"
                  variant="tonal"
                >
                  {{ $t(`user.${item.role}`) }}
                </v-chip>
              </template>
              
              <template v-slot:item.is_active="{ item }">
                <v-chip
                  :color="item.is_active ? 'success' : 'warning'"
                  variant="tonal"
                >
                  {{ $t(`user.${item.is_active ? 'active' : 'inactive'}`) }}
                </v-chip>
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  @click="deleteUser(item)"
                  :disabled="item.username === authStore.user?.username"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const authStore = useAuthStore()
const { t } = useI18n()

const users = ref([])
const loading = ref(false)
const search = ref('')

const headers = [
  { title: t('auth.username'), key: 'username', sortable: true },
  { title: t('auth.email'), key: 'email', sortable: true },
  { title: t('auth.fullName'), key: 'full_name', sortable: true },
  { title: t('user.role'), key: 'role', sortable: true },
  { title: t('user.active'), key: 'is_active', sortable: true },
  { title: t('document.uploadDate'), key: 'created_at', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false }
]

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/users/')
    users.value = response.data
  } catch (error) {
    console.error('Error loading users:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const deleteUser = async (user) => {
  if (confirm(t('user.deleteConfirm'))) {
    try {
      await api.delete(`/users/${user.id}`)
      await loadUsers()
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }
}

onMounted(() => {
  loadUsers()
})
</script>
