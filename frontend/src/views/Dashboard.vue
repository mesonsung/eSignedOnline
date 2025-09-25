<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('dashboard.welcome') }}
          </v-card-title>
          
          <v-card-text>
            <p class="text-h6 mb-4">
              {{ $t('dashboard.welcomeMessage', { username: authStore.user?.username }) }}
            </p>
            
            <v-row>
              <v-col cols="12" md="4">
                <v-card color="primary" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-file-document</v-icon>
                    <div class="text-h4">{{ stats.totalDocuments }}</div>
                    <div class="text-body-1">{{ $t('dashboard.totalDocuments') }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card color="success" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-check-circle</v-icon>
                    <div class="text-h4">{{ stats.signedDocuments }}</div>
                    <div class="text-body-1">{{ $t('dashboard.signedDocuments') }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col cols="12" md="4">
                <v-card color="warning" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-clock-outline</v-icon>
                    <div class="text-h4">{{ stats.availableDocuments }}</div>
                    <div class="text-body-1">{{ $t('dashboard.availableDocuments') }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">
            {{ $t('dashboard.recentActivity') }}
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="activity in recentActivities"
                :key="activity.id"
                :prepend-icon="activity.icon"
                :title="activity.title"
                :subtitle="activity.subtitle"
              >
                <template v-slot:append>
                  <v-chip
                    :color="activity.color"
                    size="small"
                    variant="tonal"
                  >
                    {{ activity.status }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
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

const stats = reactive({
  totalDocuments: 0,
  signedDocuments: 0,
  availableDocuments: 0
})

const recentActivities = ref([])

const loadStats = async () => {
  try {
    const response = await api.get('/documents/')
    const documents = response.data
    
    stats.totalDocuments = documents.length
    stats.signedDocuments = documents.filter(doc => doc.status === 'signed').length
    stats.availableDocuments = documents.filter(doc => doc.status === 'uploaded').length
    
    // 生成最近活動
    recentActivities.value = documents.slice(0, 5).map(doc => ({
      id: doc.id,
      icon: doc.status === 'signed' ? 'mdi-check-circle' : 'mdi-file-document',
      title: doc.original_filename,
      subtitle: `${doc.status === 'signed' ? 'Signed by' : 'Uploaded by'} ${doc.uploaded_by}`,
      status: doc.status,
      color: doc.status === 'signed' ? 'success' : 'primary'
    }))
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>
