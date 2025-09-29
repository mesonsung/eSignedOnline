<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('nav.upload') }}
          </v-card-title>
          
          <v-card-text>
            <v-form @submit.prevent="handleUpload" ref="form">
              <v-file-input
                v-model="file"
                :label="$t('document.selectFile')"
                accept=".pdf"
                :rules="fileRules"
                required
                prepend-icon="mdi-file-pdf-box"
                variant="outlined"
                class="mb-4"
              ></v-file-input>
              
              <!-- 文件大小提示 -->
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
                density="compact"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-information</v-icon>
                </template>
                <div class="text-body-2">
                  <strong>文件上傳限制：</strong>
                  <ul class="mt-2 mb-0">
                    <li>僅支援 PDF 格式</li>
                    <li>文件大小限制：50MB</li>
                    <li>建議文件大小：10MB 以下以獲得最佳上傳體驗</li>
                  </ul>
                </div>
              </v-alert>
              
              <v-btn
                type="submit"
                color="primary"
                size="large"
                :loading="uploading"
                :disabled="!file || uploading"
                prepend-icon="mdi-upload"
              >
                {{ $t('document.upload') }}
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <v-row class="mt-4">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">
            {{ $t('document.uploadedDocuments') }}
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="uploadedDocuments"
              :loading="loading"
              class="elevation-1"
            >
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
                  class="mr-2"
                ></v-btn>
                
                <v-btn
                  v-if="authStore.user?.role === 'admin'"
                  icon="mdi-delete"
                  size="small"
                  color="error"
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

const form = ref(null)
const file = ref(null)
const uploading = ref(false)
const loading = ref(false)
const uploadedDocuments = ref([])
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

const fileRules = [
  v => !!v || t('document.selectFile') + ' is required',
  v => !v || v.type === 'application/pdf' || 'Only PDF files are allowed',
  v => !v || v.size <= 50 * 1024 * 1024 || 'File size must be less than 50MB'
]

const handleUpload = async () => {
  if (!file.value) return
  
  // 檢查文件大小
  if (file.value.size > 50 * 1024 * 1024) {
    window.dispatchEvent(new CustomEvent('show-snackbar', {
      detail: {
        message: '文件大小超過 50MB 限制，請選擇較小的文件',
        color: 'error',
        timeout: 5000
      }
    }))
    return
  }
  
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    
    await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    // 清空檔案選擇
    file.value = null
    
    // 重新載入文件列表
    await loadUploadedDocuments()
    
    // 顯示成功訊息
    window.dispatchEvent(new CustomEvent('show-snackbar', {
      detail: {
        message: '文件上傳成功！',
        color: 'success',
        timeout: 3000
      }
    }))
  } catch (error) {
    console.error('Upload error:', error)
    
    let errorMessage = '文件上傳失敗'
    
    if (error.response) {
      if (error.response.status === 413) {
        errorMessage = '文件太大，請選擇小於 50MB 的文件'
      } else if (error.response.status === 400) {
        errorMessage = error.response.data?.detail || '文件格式不正確或文件損壞'
      } else if (error.response.status === 401) {
        errorMessage = '登入已過期，請重新登入'
      } else if (error.response.status === 403) {
        errorMessage = '您沒有權限上傳文件'
      } else {
        errorMessage = error.response.data?.detail || `上傳失敗 (${error.response.status})`
      }
    } else if (error.code === 'ERR_NETWORK') {
      errorMessage = '網絡連接失敗，請檢查網絡連接'
    } else if (error.message) {
      errorMessage = `上傳錯誤: ${error.message}`
    }
    
    // 顯示錯誤訊息
    window.dispatchEvent(new CustomEvent('show-snackbar', {
      detail: {
        message: errorMessage,
        color: 'error',
        timeout: 5000
      }
    }))
  } finally {
    uploading.value = false
  }
}

const loadUploadedDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents/')
    uploadedDocuments.value = response.data.filter(doc => doc.uploaded_by === authStore.user?.username && doc.status === 'uploaded')
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

const previewDocument = (doc) => {
  previewDocumentData.value = doc
  previewDialog.value = true
}

const deleteDocument = async (doc) => {
  if (confirm(t('document.deleteConfirm'))) {
    try {
      await api.delete(`/documents/${doc.id}`)
      await loadUploadedDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }
}

onMounted(() => {
  checkMobile()
  loadUploadedDocuments()
  
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
