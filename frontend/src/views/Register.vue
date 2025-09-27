<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="themed-card hover-lift pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            <span class="text-gradient">{{ $t('auth.register') }}</span>
          </v-card-title>
          
          <!-- 錯誤訊息 -->
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>
          
          <!-- 成功訊息 -->
          <v-alert
            v-if="successMessage"
            type="success"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="successMessage = ''"
          >
            {{ successMessage }}
          </v-alert>
          
          <v-form @submit.prevent="handleRegister" ref="form">
            <v-text-field
              v-model="formData.username"
              :label="$t('auth.username')"
              :rules="usernameRules"
              required
              prepend-inner-icon="mdi-account"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="formData.email"
              :label="$t('auth.email')"
              :rules="emailRules"
              required
              prepend-inner-icon="mdi-email"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="formData.fullName"
              :label="$t('auth.fullName')"
              prepend-inner-icon="mdi-account-circle"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="formData.password"
              :label="$t('auth.password')"
              :type="showPassword ? 'text' : 'password'"
              :rules="passwordRules"
              required
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="formData.confirmPassword"
              :label="$t('auth.confirmPassword')"
              :type="showConfirmPassword ? 'text' : 'password'"
              :rules="confirmPasswordRules"
              required
              prepend-inner-icon="mdi-lock-check"
              :append-inner-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showConfirmPassword = !showConfirmPassword"
              variant="outlined"
              class="mb-6"
            ></v-text-field>
            
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="loading"
            >
              {{ $t('auth.register') }}
            </v-btn>
          </v-form>
          
          <v-divider class="my-6"></v-divider>
          
          <div class="text-center">
            <p class="text-body-2 mb-2">{{ $t('auth.alreadyHaveAccount') }}</p>
            <v-btn
              variant="outlined"
              color="primary"
              @click="$router.push('/login')"
            >
              {{ $t('auth.login') }}
            </v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()

const form = ref(null)
const formData = reactive({
  username: '',
  email: '',
  fullName: '',
  password: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)
const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const usernameRules = [
  v => !!v || t('auth.validation.usernameRequired'),
  v => (v && v.length >= 3) || t('auth.validation.usernameMinLength')
]

const emailRules = [
  v => !!v || t('auth.validation.emailRequired'),
  v => /.+@.+\..+/.test(v) || t('auth.validation.emailInvalid')
]

const passwordRules = [
  v => !!v || t('auth.validation.passwordRequired'),
  v => (v && v.length >= 8) || t('auth.validation.passwordMinLength')
]

const confirmPasswordRules = [
  v => !!v || t('auth.validation.confirmPasswordRequired'),
  v => v === formData.password || t('auth.validation.passwordMismatch')
]

const handleRegister = async () => {
  if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) return
  
  // 清除之前的訊息
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true
  
  try {
    const result = await authStore.register({
      username: formData.username,
      email: formData.email,
      full_name: formData.fullName,
      password: formData.password
    })
    
    // 顯示成功訊息
    successMessage.value = result.message || '註冊成功！請檢查您的郵箱以獲取啟用碼。'
    
    // 等待一下讓用戶看到成功訊息，然後跳轉
    setTimeout(() => {
      router.push({
        path: '/activate',
        query: { username: formData.username }
      })
    }, 2000)
    
  } catch (error) {
    console.error('Register error:', error)
    
    // 從錯誤回應中提取訊息
    let errorMsg = '註冊失敗，請稍後重試'
    
    if (error.response) {
      // API 返回的錯誤
      if (error.response.data?.detail) {
        errorMsg = error.response.data.detail
      } else if (error.response.data?.errors && error.response.data.errors.length > 0) {
        // Pydantic 驗證錯誤
        const validationErrors = error.response.data.errors
        const errorMessages = validationErrors.map(err => {
          if (err.msg) {
            // 將欄位名稱翻譯為中文
            const fieldNames = {
              'username': '用戶名',
              'email': '郵箱',
              'password': '密碼',
              'full_name': '姓名'
            }
            const fieldName = fieldNames[err.loc?.[0]] || err.loc?.[0] || '欄位'
            return `${fieldName}: ${err.msg}`
          }
          return err.msg || '驗證錯誤'
        })
        errorMsg = errorMessages.join(', ')
      } else if (error.response.status === 422) {
        errorMsg = '請檢查輸入的資料格式是否正確'
      }
    } else if (error.message) {
      // 網絡錯誤或其他錯誤
      errorMsg = `網絡連接錯誤: ${error.message}`
    }
    
    errorMessage.value = errorMsg
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>
