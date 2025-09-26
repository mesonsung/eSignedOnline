<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h4">{{ $t('document.availableDocuments') }}</span>
            <v-btn
              v-if="authStore.user?.role === 'admin'"
              color="primary"
              prepend-icon="mdi-upload"
              @click="$router.push('/upload')"
            >
              {{ $t('nav.upload') }}
            </v-btn>
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="documents"
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
              
              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="item.status === 'signed' ? 'success' : 'primary'"
                  variant="tonal"
                >
                  {{ $t(`document.${item.status}`) }}
                </v-chip>
              </template>
              
              <template v-slot:item.fileSize="{ item }">
                {{ formatFileSize(item.file_size) }}
              </template>
              
              <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  @click="previewDocument(item)"
                  :hint="t('document.preview')"
                  class="mr-2"
                ></v-btn>
                
                <v-btn
                  v-if="item.status === 'uploaded' && authStore.user?.role != 'admin'"
                  icon="mdi-file-sign"
                  size="small"
                  color="success"
                  :hint="t('document.sign')"
                  @click="signDocument(item)"
                ></v-btn>
                
                <v-btn
                  v-if="item.status === 'signed' && item.signed_by === authStore.user?.username"
                  icon="mdi-download"
                  size="small"
                  color="primary"
                  :hint="t('document.download')"
                  @click="downloadDocument(item)"
                ></v-btn>
                
                <v-btn
                  v-if="authStore.user?.role === 'admin'"
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  :hint="t('document.delete')"
                  @click="deleteDocument(item)"
                ></v-btn>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- 預覽對話框 -->
    <v-dialog v-model="previewDialog" max-width="800">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ previewDocumentData?.original_filename }}</span>
          <v-btn icon="mdi-close" @click="previewDialog = false"></v-btn>
        </v-card-title>
        
        <v-card-text>
          <!-- 桌面版：使用 iframe 預覽 -->
          <div v-if="!isMobile" class="desktop-preview">
            <iframe
              v-if="previewDocumentData"
              :src="`/api/documents/${previewDocumentData.id}/preview?token=${authStore.token}`"
              width="100%"
              height="600"
              frameborder="0"
              style="border: none;"
              type="application/pdf"
              :title="$t('document.documentPreview')"
            ></iframe>
          </div>
          
          <!-- 行動版：使用 PDF.js 預覽 -->
          <div v-else class="mobile-preview">
            <div v-if="previewDocumentData" class="pdf-viewer">
              <iframe
                :src="`/api/documents/${previewDocumentData.id}/preview?token=${authStore.token}#toolbar=0&navpanes=0&scrollbar=0`"
                width="100%"
                height="500"
                frameborder="0"
                style="border: none; border-radius: 8px;"
                type="application/pdf"
                :title="$t('document.documentPreview')"
              ></iframe>
            </div>
            
            <!-- 行動版備用選項 -->
            <div class="mobile-actions mt-4">
              <v-btn
                color="primary"
                variant="outlined"
                prepend-icon="mdi-download"
                @click="downloadDocument(previewDocumentData)"
                block
              >
                {{ $t('document.download') }}
              </v-btn>
              
              <v-btn
                color="secondary"
                variant="text"
                prepend-icon="mdi-open-in-new"
                @click="openInNewTab(previewDocumentData)"
                block
                class="mt-2"
              >
                {{ $t('document.openInNewTab') }}
              </v-btn>
            </div>
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const authStore = useAuthStore()
const { t } = useI18n()

const documents = ref([])
const loading = ref(false)
const search = ref('')
const previewDialog = ref(false)
const previewDocumentData = ref(null)

// 行動裝置檢測
const isMobile = ref(false)

// 檢測是否為行動裝置
const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768 || /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 在新分頁中開啟文件
const openInNewTab = (doc) => {
  if (doc) {
    const url = `/api/documents/${doc.id}/preview?token=${authStore.token}`
    window.open(url, '_blank')
  }
}

const headers = [
  { title: t('document.originalFilename'), key: 'original_filename', sortable: true },
  { title: t('document.fileSize'), key: 'fileSize', sortable: true },
  { title: t('document.uploadDate'), key: 'created_at', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false }
]

const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents/available')
    documents.value = response.data
  } catch (error) {
    console.error('Error loading documents:', error)
  } finally {
    loading.value = false
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const previewDocument = (doc) => {
  previewDocumentData.value = doc
  previewDialog.value = true
}

const signDocument = (doc) => {
  // 直接跳轉到簽署頁面（可簽署文件）
  window.location.href = `/sign/${doc.id}`
}

const downloadDocument = async (doc) => {
  try {
    const response = await api.get(`/documents/${doc.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', doc.signed_filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Error downloading document:', error)
  }
}

const deleteDocument = async (doc) => {
  if (confirm(t('document.deleteConfirm'))) {
    try {
      await api.delete(`/documents/${doc.id}`)
      await loadDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const tmep = dateString.split('.')[0]+'Z'
  const d = new Date(tmep)
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone // Uses local time zone
  };
  const localDate = d.toLocaleString('zh-TW', options)
  return localDate
}

onMounted(() => {
  checkMobile()
  loadDocuments()
  
  // 監聽視窗大小變化
  window.addEventListener('resize', checkMobile)
})

// 清理事件監聽器
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.text-grey {
  color: #9e9e9e;
}

/* 行動裝置預覽樣式 */
.mobile-preview {
  padding: 8px;
}

.pdf-viewer {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 16px;
}

.mobile-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.desktop-preview {
  padding: 8px;
}

/* 響應式設計 */
@media (max-width: 768px) {
  .mobile-preview {
    padding: 4px;
  }
  
  .pdf-viewer {
    padding: 4px;
  }
  
  .pdf-viewer iframe {
    height: 400px !important;
  }
}
</style>
