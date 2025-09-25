<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" class="pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            {{ $t('auth.register') }}
          </v-card-title>
          
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

const usernameRules = [
  v => !!v || t('auth.username') + ' is required',
  v => (v && v.length >= 3) || 'Username must be at least 3 characters'
]

const emailRules = [
  v => !!v || t('auth.email') + ' is required',
  v => /.+@.+\..+/.test(v) || 'Email must be valid'
]

const passwordRules = [
  v => !!v || t('auth.password') + ' is required',
  v => (v && v.length >= 6) || 'Password must be at least 6 characters'
]

const confirmPasswordRules = [
  v => !!v || 'Please confirm your password',
  v => v === formData.password || 'Passwords do not match'
]

const handleRegister = async () => {
  if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) return
  
  loading.value = true
  
  try {
    await authStore.register({
      username: formData.username,
      email: formData.email,
      full_name: formData.fullName,
      password: formData.password
    })
    
    // 註冊成功後跳轉到啟用頁面
    router.push({
      path: '/activate',
      query: { username: formData.username }
    })
  } catch (error) {
    console.error('Register error:', error)
    // 這裡可以顯示錯誤訊息
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
