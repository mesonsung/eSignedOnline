<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span class="text-h4">{{ $t('nav.documents') }}</span>
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
              
              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  @click="previewDocument(item)"
                  :hint="t('document.preview')"
                  class="mr-2"
                ></v-btn>
                
                <v-btn
                  v-if="item.status === 'uploaded'"
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
          <iframe
            v-if="previewDocumentData"
            :src="`/api/documents/${previewDocumentData.id}/preview?token=${authStore.token}`"
            width="100%"
            height="600"
            frameborder="0"
            style="border: none;"
            type="application/pdf"
            title="PDF Preview"
          ></iframe>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
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

const headers = [
  { title: t('document.originalFilename'), key: 'original_filename', sortable: true },
  { title: t('document.fileSize'), key: 'fileSize', sortable: true },
  { title: t('document.status'), key: 'status', sortable: true },
  { title: t('document.uploadedBy'), key: 'uploaded_by', sortable: true },
  { title: t('document.signedBy'), key: 'signed_by', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false }
]

const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents/')
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

const previewDocument = (document) => {
  previewDocumentData.value = document
  previewDialog.value = true
}

const signDocument = (document) => {
  // 跳轉到簽署頁面
  window.location.href = `/sign/${document.id}`
}

const downloadDocument = async (document) => {
  try {
    const response = await api.get(`/documents/${document.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', document.signed_filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Error downloading document:', error)
  }
}

const deleteDocument = async (document) => {
  if (confirm(t('document.deleteConfirm'))) {
    try {
      await api.delete(`/documents/${document.id}`)
      await loadDocuments()
    } catch (error) {
      console.error('Error deleting document:', error)
    }
  }
}

onMounted(() => {
  loadDocuments()
})
</script>
