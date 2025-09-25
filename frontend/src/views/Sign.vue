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
                      
                      <!-- 簽名畫布 -->
                      <div class="mt-4">
                        <v-label class="text-subtitle-1 mb-2">{{ $t('document.signature') }}</v-label>
                        <v-card variant="outlined" class="signature-card">
                          <canvas
                            ref="signatureCanvas"
                            width="400"
                            height="150"
                            class="signature-canvas"
                            @mousedown="startDrawing"
                            @mousemove="draw"
                            @mouseup="stopDrawing"
                            @mouseleave="stopDrawing"
                            @touchstart="startDrawing"
                            @touchmove="draw"
                            @touchend="stopDrawing"
                          ></canvas>
                          <v-card-actions>
                            <v-btn
                              color="error"
                              variant="text"
                              size="small"
                              @click="clearSignature"
                            >
                              {{ $t('common.clear') }}
                            </v-btn>
                          </v-card-actions>
                        </v-card>
                      </div>
                      
                      <div class="text-center mt-4">
                        <v-btn
                          color="primary"
                          size="large"
                          :loading="signing"
                          :disabled="!signature.name || !hasSignature || signing"
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
import { ref, reactive, onMounted, nextTick } from 'vue'
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
const signatureCanvas = ref(null)
const hasSignature = ref(false)

// 簽名畫布相關變量
let isDrawing = false
let lastX = 0
let lastY = 0

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

// 簽名畫布功能
const initCanvas = () => {
  if (signatureCanvas.value) {
    const canvas = signatureCanvas.value
    const ctx = canvas.getContext('2d')
    
    // 設置畫布樣式
    ctx.strokeStyle = '#000000'
    ctx.lineWidth = 2
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
    
    // 設置白色背景
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }
}

const startDrawing = (e) => {
  isDrawing = true
  const canvas = signatureCanvas.value
  const rect = canvas.getBoundingClientRect()
  
  if (e.type === 'mousedown') {
    lastX = e.clientX - rect.left
    lastY = e.clientY - rect.top
  } else if (e.type === 'touchstart') {
    e.preventDefault()
    const touch = e.touches[0]
    lastX = touch.clientX - rect.left
    lastY = touch.clientY - rect.top
  }
}

const draw = (e) => {
  if (!isDrawing) return
  
  const canvas = signatureCanvas.value
  const ctx = canvas.getContext('2d')
  const rect = canvas.getBoundingClientRect()
  
  let currentX, currentY
  
  if (e.type === 'mousemove') {
    currentX = e.clientX - rect.left
    currentY = e.clientY - rect.top
  } else if (e.type === 'touchmove') {
    e.preventDefault()
    const touch = e.touches[0]
    currentX = touch.clientX - rect.left
    currentY = touch.clientY - rect.top
  }
  
  ctx.beginPath()
  ctx.moveTo(lastX, lastY)
  ctx.lineTo(currentX, currentY)
  ctx.stroke()
  
  lastX = currentX
  lastY = currentY
  
  hasSignature.value = true
}

const stopDrawing = () => {
  isDrawing = false
}

const clearSignature = () => {
  if (signatureCanvas.value) {
    const canvas = signatureCanvas.value
    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    hasSignature.value = false
  }
}

const getSignatureImage = () => {
  if (signatureCanvas.value) {
    return signatureCanvas.value.toDataURL('image/png')
  }
  return null
}

const handleSign = async () => {
  if (!signature.name || !hasSignature.value) return
  
  signing.value = true
  
  try {
    // 獲取簽名圖像
    const signatureImage = getSignatureImage()
    
    // 創建簽名數據
    const signatureData = {
      name: signature.name,
      title: signature.title,
      reason: signature.reason,
      timestamp: new Date().toISOString(),
      signature_image: signatureImage
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

onMounted(async () => {
  await loadDocument()
  await nextTick()
  initCanvas()
})
</script>

<style scoped>
.signature-card {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.signature-canvas {
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: crosshair;
  background-color: white;
  display: block;
  margin: 0 auto;
}

.signature-canvas:hover {
  border-color: #1976d2;
}

/* 響應式設計 */
@media (max-width: 600px) {
  .signature-canvas {
    width: 100%;
    max-width: 350px;
    height: 120px;
  }
}
</style>
