<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h4 mb-4">
            {{ $t('document.sign') }}
          </v-card-title>
          
          <v-card-text>
            <div v-if="loading" class="text-center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <p class="mt-2">{{ $t('common.loading') }}</p>
            </div>
            
            <div v-else-if="document">
              <v-row>
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-title>{{ $t('document.documentInfo') }}</v-card-title>
                    <v-card-text>
                      <v-list>
                        <v-list-item>
                          <v-list-item-title>{{ $t('document.originalFilename') }}</v-list-item-title>
                          <v-list-item-subtitle>{{ document.original_filename }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>{{ $t('document.fileSize') }}</v-list-item-title>
                          <v-list-item-subtitle>{{ formatFileSize(document.file_size) }}</v-list-item-subtitle>
                        </v-list-item>
                        <v-list-item>
                          <v-list-item-title>{{ $t('document.uploadedBy') }}</v-list-item-title>
                          <v-list-item-subtitle>{{ document.uploaded_by }}</v-list-item-subtitle>
                        </v-list-item>
                      </v-list>
                    </v-card-text>
                  </v-card>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-card variant="outlined">
                    <v-card-title>{{ $t('document.preview') }}</v-card-title>
                    <v-card-text>
                      <iframe
                        :src="`/api/documents/${document.id}/preview?token=${authStore.token}`"
                        width="100%"
                        height="400"
                        frameborder="0"
                        style="border: none;"
                        type="application/pdf"
                        title="PDF Preview"
                      ></iframe>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined">
                    <v-card-title>{{ $t('document.signature') }}</v-card-title>
                    <v-card-text>
                      <v-row>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="signature.name"
                            :label="$t('document.signatureName')"
                            variant="outlined"
                            required
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="6">
                          <v-text-field
                            v-model="signature.title"
                            :label="$t('document.signatureTitle')"
                            variant="outlined"
                          ></v-text-field>
                        </v-col>
                      </v-row>
                      
                      <v-textarea
                        v-model="signature.reason"
                        :label="$t('document.signatureReason')"
                        variant="outlined"
                        rows="3"
                      ></v-textarea>
                      
                      <div class="text-center mt-4">
                        <v-btn
                          color="primary"
                          size="large"
                          :loading="signing"
                          :disabled="!signature.name || signing"
                          @click="handleSign"
                          prepend-icon="mdi-file-sign"
                        >
                          {{ $t('document.sign') }}
                        </v-btn>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </div>
            
            <div v-else class="text-center">
              <v-icon size="64" color="error">mdi-file-question</v-icon>
              <p class="text-h6 mt-2">{{ $t('document.notFound') }}</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const document = ref(null)
const loading = ref(false)
const signing = ref(false)

const signature = reactive({
  name: '',
  title: '',
  reason: ''
})

const loadDocument = async () => {
  loading.value = true
  try {
    const response = await api.get(`/documents/${route.params.id}`)
    document.value = response.data
  } catch (error) {
    console.error('Error loading document:', error)
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

const handleSign = async () => {
  if (!signature.name) return
  
  signing.value = true
  
  try {
    // 創建簽名數據
    const signatureData = {
      name: signature.name,
      title: signature.title,
      reason: signature.reason,
      timestamp: new Date().toISOString()
    }
    
    await api.post(`/documents/${route.params.id}/sign`, {
      signature_data: JSON.stringify(signatureData)
    })
    
    // 簽署成功後跳轉到文件列表
    router.push('/documents')
  } catch (error) {
    console.error('Sign error:', error)
  } finally {
    signing.value = false
  }
}

onMounted(() => {
  loadDocument()
})
</script>
