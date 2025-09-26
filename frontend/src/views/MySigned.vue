<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('document.signedDocuments') }}
          </v-card-title>
          
          <v-card-text>
            <v-data-table
              :headers="headers"
              :items="signedDocuments"
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
              
              <template v-slot:item.fileSize="{ item }">
                {{ formatFileSize(item.file_size) }}
              </template>
              
              <template v-slot:item.signed_by="{ item }">
                <span v-if="item.signed_by">
                  {{ item.signed_by }}
                </span>
                <span v-else class="text-grey">-</span>
              </template>
              
              <template v-slot:item.signDate="{ item }">
                {{ formatDate(item.updated_at) }}
              </template>
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  @click="previewDocument(item)"
                  class="mr-2"
                ></v-btn>
                
                <v-btn
                  icon="mdi-download"
                  size="small"
                  color="primary"
                  @click="downloadDocument(item)"
                  class="mr-2"
                ></v-btn>
                
                <!-- 管理員可以刪除所有已簽署文件，一般用戶只能刪除自己簽署的文件 -->
                <v-btn
                  v-if="authStore.user?.role === 'admin' || item.signed_by === authStore.user?.username"
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
          <span>{{ previewDocumentData?.signed_filename }}</span>
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
    
    <!-- 簽名預覽對話框 -->
    <v-dialog v-model="signatureDialog" max-width="500">
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <span>{{ $t('document.signaturePreview') }}</span>
          <v-btn icon="mdi-close" @click="signatureDialog = false"></v-btn>
        </v-card-title>
        
        <v-card-text>
          <div v-if="signatureDialogData" class="text-center">
            <img 
              :src="getSignatureImage(signatureDialogData.signature_data)" 
              :alt="$t('document.signature')"
              class="signature-full"
            />
            <div class="mt-4">
              <p><strong>{{ $t('document.signatureName') }}:</strong> {{ getSignatureInfo(signatureDialogData.signature_data)?.name || '-' }}</p>
              <p><strong>{{ $t('document.signDate') }}:</strong> {{ formatDate(getSignatureInfo(signatureDialogData.signature_data)?.timestamp) }}</p>
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

const signedDocuments = ref([])
const loading = ref(false)
const search = ref('')
const previewDialog = ref(false)
const previewDocumentData = ref(null)
const signatureDialog = ref(false)
const signatureDialogData = ref(null)

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
  { title: t('document.signedFilename'), key: 'signed_filename', sortable: true },
  { title: t('document.originalFilename'), key: 'original_filename', sortable: true },
  { title: t('document.fileSize'), key: 'fileSize', sortable: true },
  { title: t('document.signedBy'), key: 'signed_by', sortable: true },
  { title: t('document.signDate'), key: 'signDate', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false }
]

const loadSignedDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents/all-signed')
    signedDocuments.value = response.data
  } catch (error) {
    console.error('Error loading signed documents:', error)
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

const getSignatureImage = (signatureData) => {
  try {
    if (typeof signatureData === 'string') {
      const parsed = JSON.parse(signatureData)
      return parsed.signature_image || signatureData
    }
    return signatureData.signature_image || signatureData
  } catch (error) {
    // 如果不是 JSON 格式，直接返回
    return signatureData
  }
}

const getSignatureInfo = (signatureData) => {
  try {
    if (typeof signatureData === 'string') {
      return JSON.parse(signatureData)
    }
    return signatureData
  } catch (error) {
    return null
  }
}

const showSignatureDialog = (doc) => {
  signatureDialogData.value = doc
  signatureDialog.value = true
}

const deleteDocument = async (doc) => {
  if (confirm(t('document.deleteSignedConfirm'))) {
    try {
      await api.delete(`/documents/${doc.id}`)
      await loadSignedDocuments()
      
      // 顯示成功通知
      const event = new CustomEvent('show-snackbar', {
        detail: {
          message: t('document.deleteSignedSuccess'),
          color: 'success',
          timeout: 3000
        }
      })
      window.dispatchEvent(event)
    } catch (error) {
      console.error('Error deleting document:', error)
      
      // 顯示錯誤通知
      const event = new CustomEvent('show-snackbar', {
        detail: {
          message: t('document.deleteError'),
          color: 'error',
          timeout: 5000
        }
      })
      window.dispatchEvent(event)
    }
  }
}

onMounted(() => {
  checkMobile()
  loadSignedDocuments()
  
  // 監聽視窗大小變化
  window.addEventListener('resize', checkMobile)
})

// 清理事件監聽器
onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.signature-preview {
  display: flex;
  justify-content: center;
  align-items: center;
}

.signature-thumbnail {
  width: 60px;
  height: 30px;
  object-fit: contain;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  background-color: white;
  transition: all 0.2s ease;
}

.signature-thumbnail:hover {
  border-color: #1976d2;
  transform: scale(1.1);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.signature-full {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
  border: 2px solid #ddd;
  border-radius: 8px;
  background-color: white;
  padding: 16px;
}

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
