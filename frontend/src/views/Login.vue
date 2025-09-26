<template>
  <v-container fluid class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="8" class="pa-6">
          <v-card-title class="text-h4 text-center mb-6">
            {{ $t('auth.login') }}
          </v-card-title>
          
          <v-form @submit.prevent="handleLogin" ref="form">
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
              v-model="formData.password"
              :label="$t('auth.password')"
              :type="showPassword ? 'text' : 'password'"
              :rules="passwordRules"
              required
              prepend-inner-icon="mdi-lock"
              :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append-inner="showPassword = !showPassword"
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
              {{ $t('auth.login') }}
            </v-btn>
          </v-form>
          
          <v-divider class="my-6"></v-divider>
          
          <div class="text-center">
            <p class="text-body-2 mb-2">{{ $t('auth.donotHaveAccount') }}</p>
            <v-btn
              variant="outlined"
              color="primary"
              @click="$router.push('/register')"
            >
              {{ $t('auth.register') }}
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
  password: ''
})

const showPassword = ref(false)
const loading = ref(false)

const usernameRules = [
  v => !!v || t('auth.validation.usernameRequired')
]

const passwordRules = [
  v => !!v || t('auth.validation.passwordRequired')
]

const handleLogin = async () => {
  if (!formData.username || !formData.password) return
  
  loading.value = true
  
  try {
    await authStore.login(formData)
    router.push('/dashboard')
  } catch (error) {
    console.error('Login error:', error)
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
