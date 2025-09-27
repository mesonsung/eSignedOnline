<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="themed-card hover-lift pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            <span class="text-gradient">{{ $t('forgotPassword.title') }}</span>
          </v-card-title>
          
          <v-card-subtitle class="text-center mb-4">
            {{ $t('forgotPassword.subtitle') }}
          </v-card-subtitle>
          
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
          
          <!-- 發送重設郵件表單 -->
          <v-form v-if="!emailSent" @submit.prevent="handleForgotPassword" ref="form">
            <v-text-field
              v-model="email"
              :label="$t('auth.email')"
              :rules="emailRules"
              required
              prepend-inner-icon="mdi-email"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-btn
              type="submit"
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="loading"
              prepend-icon="mdi-email-send"
            >
              {{ $t('forgotPassword.sendResetEmail') }}
            </v-btn>
          </v-form>
          
          <!-- 輸入重設碼表單 -->
          <v-form v-else @submit.prevent="handleResetPassword" ref="resetForm">
            <v-text-field
              v-model="resetData.token"
              :label="$t('forgotPassword.resetCode')"
              :rules="tokenRules"
              required
              prepend-inner-icon="mdi-key"
              variant="outlined"
              class="mb-4"
            ></v-text-field>
            
            <v-text-field
              v-model="resetData.newPassword"
              :label="$t('forgotPassword.newPassword')"
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
              v-model="resetData.confirmPassword"
              :label="$t('forgotPassword.confirmPassword')"
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
              :loading="resetLoading"
              :disabled="resetLoading"
              prepend-icon="mdi-key-change"
            >
              {{ $t('forgotPassword.resetPassword') }}
            </v-btn>
            
            <v-btn
              variant="text"
              color="primary"
              block
              class="mt-4"
              @click="goBackToEmailForm"
              prepend-icon="mdi-arrow-left"
            >
              {{ $t('forgotPassword.backToEmail') }}
            </v-btn>
          </v-form>
          
          <v-divider class="my-6"></v-divider>
          
          <div class="text-center">
            <p class="text-body-2 mb-2">{{ $t('forgotPassword.rememberPassword') }}</p>
            <v-btn
              variant="outlined"
              color="primary"
              @click="$router.push('/login')"
              prepend-icon="mdi-arrow-left"
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
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const router = useRouter()
const { t } = useI18n()

const form = ref(null)
const resetForm = ref(null)
const email = ref('')
const emailSent = ref(false)
const loading = ref(false)
const resetLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const resetData = reactive({
  token: '',
  newPassword: '',
  confirmPassword: ''
})

const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 驗證規則
const emailRules = [
  v => !!v || t('auth.validation.emailRequired'),
  v => /.+@.+\..+/.test(v) || t('auth.validation.emailInvalid')
]

const tokenRules = [
  v => !!v || t('forgotPassword.validation.tokenRequired')
]

const passwordRules = [
  v => !!v || t('forgotPassword.validation.passwordRequired'),
  v => (v && v.length >= 6) || t('forgotPassword.validation.passwordMinLength')
]

const confirmPasswordRules = [
  v => !!v || t('forgotPassword.validation.confirmPasswordRequired'),
  v => v === resetData.newPassword || t('forgotPassword.validation.passwordMismatch')
]

// 發送重設密碼郵件
const handleForgotPassword = async () => {
  if (!email.value) return
  
  // 清除之前的訊息
  errorMessage.value = ''
  successMessage.value = ''
  loading.value = true
  
  try {
    const response = await api.post('/auth/forgot-password', {
      email: email.value
    })
    
    // 顯示成功訊息並切換到重設表單
    successMessage.value = response.data.message
    emailSent.value = true
    
  } catch (error) {
    console.error('發送重設密碼郵件失敗:', error)
    
    let errorMsg = '發送重設郵件失敗，請稍後重試'
    
    if (error.response && error.response.data?.detail) {
      errorMsg = error.response.data.detail
    }
    
    errorMessage.value = errorMsg
  } finally {
    loading.value = false
  }
}

// 重設密碼
const handleResetPassword = async () => {
  if (!resetData.token || !resetData.newPassword || !resetData.confirmPassword) return
  
  // 清除之前的訊息
  errorMessage.value = ''
  successMessage.value = ''
  resetLoading.value = true
  
  try {
    const response = await api.post('/auth/reset-password', {
      token: resetData.token,
      new_password: resetData.newPassword
    })
    
    // 顯示成功訊息
    successMessage.value = response.data.message
    
    // 等待一下讓用戶看到成功訊息，然後跳轉到登入頁面
    setTimeout(() => {
      router.push('/login')
    }, 2000)
    
  } catch (error) {
    console.error('重設密碼失敗:', error)
    
    let errorMsg = '重設密碼失敗，請檢查重設碼是否正確'
    
    if (error.response && error.response.data?.detail) {
      errorMsg = error.response.data.detail
    }
    
    errorMessage.value = errorMsg
  } finally {
    resetLoading.value = false
  }
}

// 返回郵件輸入表單
const goBackToEmailForm = () => {
  emailSent.value = false
  resetData.token = ''
  resetData.newPassword = ''
  resetData.confirmPassword = ''
  errorMessage.value = ''
  successMessage.value = ''
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-card {
  border-radius: 12px;
}
</style>
