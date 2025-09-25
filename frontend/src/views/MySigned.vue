<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('nav.my-signed') }}
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
                {{ formatFileSize(item.fileSize) }}
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

const signedDocuments = ref([])
const loading = ref(false)
const search = ref('')
const previewDialog = ref(false)
const previewDocumentData = ref(null)

const headers = [
  { title: t('document.signedFilename'), key: 'signed_filename', sortable: true },
  { title: t('document.originalFilename'), key: 'original_filename', sortable: true },
  { title: t('document.fileSize'), key: 'fileSize', sortable: true },
  { title: t('document.signDate'), key: 'signDate', sortable: true },
  { title: t('common.actions'), key: 'actions', sortable: false }
]

const loadSignedDocuments = async () => {
  loading.value = true
  try {
    const response = await api.get('/documents/signed')
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
  return new Date(dateString).toLocaleDateString()
}

const previewDocument = (document) => {
  previewDocumentData.value = document
  previewDialog.value = true
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

onMounted(() => {
  loadSignedDocuments()
})
</script>
