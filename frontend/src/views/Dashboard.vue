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
              <!-- 管理員可以看到總文件數 -->
              <v-col v-if="authStore.user?.role === 'admin'" cols="12" md="4">
                <v-card color="primary" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-file-document</v-icon>
                    <div class="text-h4">{{ stats.totalDocuments }}</div>
                    <div class="text-body-1">{{ $t('dashboard.totalDocuments') }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col :cols="authStore.user?.role === 'admin' ? '12' : '6'" :md="authStore.user?.role === 'admin' ? '4' : '6'">
                <v-card color="success" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-check-circle</v-icon>
                    <div class="text-h4">{{ stats.signedDocuments }}</div>
                    <div class="text-body-1">
                      {{ $t('dashboard.signedDocuments') }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
              
              <v-col :cols="authStore.user?.role === 'admin' ? '12' : '6'" :md="authStore.user?.role === 'admin' ? '4' : '6'">
                <v-card color="warning" variant="tonal">
                  <v-card-text class="text-center">
                    <v-icon size="48" class="mb-2">mdi-clock-outline</v-icon>
                    <div class="text-h4">{{ stats.availableDocuments }}</div>
                    <div class="text-body-1">
                      {{ authStore.user?.role === 'admin' ? $t('dashboard.availableDocuments') : $t('dashboard.documentsToSign') }}
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- 只有管理員可以看到最近的活動 -->
    <v-row v-if="authStore.user?.role === 'admin'" class="mt-4">
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
    // 獲取所有文件（用於總數和最近活動）
    const allDocumentsResponse = await api.get('/documents/')
    const allDocuments = allDocumentsResponse.data
    
    // 獲取可簽署文件（未簽署的文件）
    const availableDocumentsResponse = await api.get('/documents/available')
    const availableDocuments = availableDocumentsResponse.data
    
    // 設置統計數據
    if (authStore.user?.role === 'admin') {
      stats.totalDocuments = allDocuments.length
      // 管理員看到所有已簽署文件
      stats.signedDocuments = allDocuments.filter(doc => doc.status === 'signed').length
    } else {
      // 一般用戶看到所有已簽署文件（使用新的 API）
      const allSignedDocumentsResponse = await api.get('/documents/all-signed')
      const allSignedDocuments = allSignedDocumentsResponse.data
      stats.signedDocuments = allSignedDocuments.length
    }
    
    // 可簽署文件數量
    stats.availableDocuments = availableDocuments.length
    
    // 生成最近活動 - 只有管理員需要
    if (authStore.user?.role === 'admin') {
      recentActivities.value = allDocuments.slice(0, 5).map(doc => ({
        id: doc.id,
        icon: doc.status === 'signed' ? 'mdi-check-circle' : 'mdi-file-document',
        title: doc.original_filename,
        subtitle: `${doc.status === 'signed' ? 'Signed by ' + doc.signed_by : 'Uploaded by ' + doc.uploaded_by}`,
        status: doc.status,
        color: doc.status === 'signed' ? 'success' : 'primary'
      }))
    }
  } catch (error) {
    console.error('Error loading stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>
