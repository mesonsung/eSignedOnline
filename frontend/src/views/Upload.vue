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
              <!-- 拖拽上傳區域 -->
              <div
                class="upload-drop-zone mb-4"
                :class="{ 'drag-over': isDragOver, 'uploading': uploading }"
                @dragover.prevent="handleDragOver"
                @dragleave.prevent="handleDragLeave"
                @drop.prevent="handleDrop"
                @click="triggerFileInput"
              >
                <div class="text-center pa-8">
                  <v-icon 
                    size="48" 
                    :color="isDragOver ? 'primary' : 'grey'"
                    class="mb-4"
                  >
                    mdi-cloud-upload
                  </v-icon>
                  <div class="text-h6 mb-2">
                    {{ isDragOver ? '放開文件開始上傳' : '拖拽 PDF 文件到這裡' }}
                  </div>
                  <div class="text-body-2 text-grey">
                    或點擊選擇文件
                  </div>
                  <div v-if="file" class="mt-4">
                    <v-chip color="primary" variant="tonal">
                      <v-icon start>mdi-file-pdf-box</v-icon>
                      {{ file.name }} ({{ formatBytes(file.size) }})
                    </v-chip>
                  </div>
                </div>
              </div>
              
              <!-- 隱藏的文件輸入 -->
              <input
                ref="fileInput"
                type="file"
                accept=".pdf"
                @change="handleFileSelect"
                style="display: none"
              />
              
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
              
              <!-- 上傳進度條 -->
              <v-progress-linear
                v-if="uploading && uploadProgress > 0"
                :model-value="uploadProgress"
                color="primary"
                height="8"
                rounded
                class="mb-4"
              >
                <template v-slot:default="{ value }">
                  <strong>{{ Math.ceil(value) }}%</strong>
                </template>
              </v-progress-linear>
              
              <!-- 上傳狀態訊息 -->
              <v-alert
                v-if="uploading"
                type="info"
                variant="tonal"
                class="mb-4"
                density="compact"
              >
                <template v-slot:prepend>
                  <v-progress-circular
                    indeterminate
                    size="20"
                    color="primary"
                  ></v-progress-circular>
                </template>
                <div class="text-body-2">
                  <strong>正在上傳文件...</strong>
                  <div v-if="uploadProgress > 0" class="mt-1">
                    進度：{{ Math.ceil(uploadProgress) }}% 
                    <span v-if="uploadSpeed">({{ uploadSpeed }})</span>
                  </div>
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
                {{ uploading ? '上傳中...' : $t('document.upload') }}
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

// 上傳進度相關
const uploadProgress = ref(0)
const uploadSpeed = ref('')
const uploadStartTime = ref(null)

// 拖拽相關
const isDragOver = ref(false)
const fileInput = ref(null)

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

// 拖拽處理函數
const handleDragOver = (event) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event) => {
  event.preventDefault()
  isDragOver.value = false
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragOver.value = false
  
  const droppedFiles = event.dataTransfer.files
  if (droppedFiles.length > 0) {
    const droppedFile = droppedFiles[0]
    if (droppedFile.type === 'application/pdf') {
      file.value = droppedFile
    } else {
      window.dispatchEvent(new CustomEvent('show-snackbar', {
        detail: {
          message: '只支援 PDF 文件格式',
          color: 'error',
          timeout: 3000
        }
      }))
    }
  }
}

const triggerFileInput = () => {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event) => {
  const selectedFile = event.target.files[0]
  if (selectedFile) {
    file.value = selectedFile
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

// 格式化文件大小
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 計算上傳速度
const calculateUploadSpeed = (loaded, total, startTime) => {
  const elapsed = (Date.now() - startTime) / 1000 // 秒
  if (elapsed === 0) return ''
  
  const speed = loaded / elapsed // bytes per second
  const remaining = total - loaded
  const eta = remaining / speed
  
  let speedText = formatBytes(speed) + '/s'
  if (eta < 60) {
    speedText += ` (剩餘 ${Math.ceil(eta)}秒)`
  } else {
    speedText += ` (剩餘 ${Math.ceil(eta / 60)}分鐘)`
  }
  
  return speedText
}

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
  
  // 重置進度
  uploadProgress.value = 0
  uploadSpeed.value = ''
  uploadStartTime.value = Date.now()
  uploading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', file.value)
    
    await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = (progressEvent.loaded * 100) / progressEvent.total
          uploadSpeed.value = calculateUploadSpeed(
            progressEvent.loaded,
            progressEvent.total,
            uploadStartTime.value
          )
        }
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
    uploadProgress.value = 0
    uploadSpeed.value = ''
    uploadStartTime.value = null
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

/* 拖拽上傳區域樣式 */
.upload-drop-zone {
  border: 2px dashed #ccc;
  border-radius: 12px;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-drop-zone:hover {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.upload-drop-zone.drag-over {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.1);
  transform: scale(1.02);
}

.upload-drop-zone.uploading {
  border-color: rgb(var(--v-theme-primary));
  background-color: rgba(var(--v-theme-primary), 0.05);
  cursor: not-allowed;
}

.upload-drop-zone.uploading:hover {
  transform: none;
}

/* 移動設備優化 */
@media (max-width: 600px) {
  .upload-drop-zone {
    min-height: 150px;
    padding: 16px;
  }
  
  .upload-drop-zone .text-h6 {
    font-size: 16px !important;
  }
  
  .upload-drop-zone .text-body-2 {
    font-size: 14px !important;
  }
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
