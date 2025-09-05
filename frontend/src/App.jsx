import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Sparkles, Brain, Zap, MessageCircle, Copy, Check, Settings, Bot, Github, Twitter, Linkedin, ExternalLink } from 'lucide-react'

function App() {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [selectedModel, setSelectedModel] = useState('gemma')
  const [availableModels, setAvailableModels] = useState({})
  const [currentModel, setCurrentModel] = useState('')
  const [startTime, setStartTime] = useState(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const [responseTime, setResponseTime] = useState(null)
  const messagesEndRef = useRef(null)
  const timerRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Fetch available models on component mount
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/models')
        if (response.ok) {
          const data = await response.json()
          setAvailableModels(data.available_models)
          setCurrentModel(data.current_model)
          // Set default selection to current model
          const modelKey = Object.keys(data.available_models).find(key => 
            data.available_models[key] === data.current_model
          )
          if (modelKey) setSelectedModel(modelKey)
        }
      } catch (error) {
        console.error('Failed to fetch models:', error)
      }
    }
    fetchModels()
  }, [])

  // Timer effect for tracking elapsed time
  useEffect(() => {
    if (isLoading && startTime) {
      timerRef.current = setInterval(() => {
        setElapsedTime(Date.now() - startTime)
      }, 100) // Update every 100ms for smooth display
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [isLoading, startTime])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!prompt.trim()) return

    const userMessage = { type: 'user', content: prompt, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setPrompt('')
    setIsLoading(true)
    
    // Start timer
    const requestStartTime = Date.now()
    setStartTime(requestStartTime)
    setElapsedTime(0)
    setResponseTime(null)

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          prompt,
          model: availableModels[selectedModel] || selectedModel
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      
      // Calculate final response time
      const finalResponseTime = Date.now() - requestStartTime
      setResponseTime(finalResponseTime)
      
      const aiMessage = { 
        type: 'ai', 
        content: data.response, 
        timestamp: new Date(),
        responseTime: finalResponseTime
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      const errorMessage = { 
        type: 'error', 
        content: `Error: ${error.message}. Make sure the backend is running and the API key is correct.`, 
        timestamp: new Date() 
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const clearChat = () => {
    setMessages([])
    setResponseTime(null)
    setElapsedTime(0)
    setStartTime(null)
  }

  const formatTime = (milliseconds) => {
    if (milliseconds < 1000) {
      return `${milliseconds}ms`
    } else {
      return `${(milliseconds / 1000).toFixed(1)}s`
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50"
      >
        <div className="max-w-5xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-black rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                Affordable Self-Hosted AI Magic: GPU-Free API Powered by Google & Qwen!
                </h1>
                <p className="text-sm text-gray-500">Powered by {currentModel || 'AI Model'}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Model Selector */}
              <div className="flex items-center space-x-2">
                <Settings className="w-4 h-4 text-gray-400" />
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="border border-gray-200 rounded-lg px-3 py-1 text-gray-700 text-sm focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent bg-white"
                >
                  {Object.entries(availableModels).map(([key, value]) => (
                    <option key={key} value={key}>
                      {key === 'gemma' ? 'Gemma' : key === 'qwen' ? 'Qwen' : key.charAt(0).toUpperCase() + key.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                onClick={clearChat}
                className="px-4 py-2 border border-gray-200 hover:bg-gray-50 rounded-lg text-gray-700 text-sm transition-colors"
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              One Prompt. One AI Response.
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Enter a prompt and get intelligent responses from our self-hosted AI model.
            </p>
          </motion.div>
        )}

        {/* Messages */}
        {messages.length > 0 && (
          <div className="space-y-8 mb-8">
            <AnimatePresence>
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-4"
                >
                  {message.type === 'user' && (
                    <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center flex-shrink-0">
                          <MessageCircle className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 mb-2">Your Prompt</h3>
                          <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {message.type === 'ai' && (
                    <div className="bg-white rounded-2xl p-6 border border-gray-200">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                          <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-3">
                              <h3 className="font-medium text-gray-900">AI Response</h3>
                              {message.responseTime && (
                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                  {formatTime(message.responseTime)}
                                </span>
                              )}
                            </div>
                            <button
                              onClick={() => copyToClipboard(message.content)}
                              className="p-1 hover:bg-gray-100 rounded text-sm flex items-center space-x-1 text-gray-500 hover:text-gray-700 transition-colors"
                            >
                              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                              <span>{copied ? 'Copied!' : 'Copy'}</span>
                            </button>
                          </div>
                          <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {message.type === 'error' && (
                    <div className="bg-red-50 rounded-2xl p-6 border border-red-200">
                      <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0">
                          <Zap className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-red-900 mb-2">Error</h3>
                          <p className="text-red-700 whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        </div>
                      </div>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-2xl p-6 border border-gray-200"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="font-medium text-gray-900">AI is thinking...</h3>
                      {elapsedTime > 0 && (
                        <span className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full animate-pulse">
                          {formatTime(elapsedTime)}
                        </span>
                      )}
                    </div>
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl border border-gray-200 shadow-lg"
        >
          <form onSubmit={handleSubmit} className="p-6">
            <div className="space-y-4">
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Enter your prompt here..."
                className="w-full px-0 py-0 border-0 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-0 resize-none text-lg leading-relaxed"
                rows="6"
                style={{ minHeight: '150px' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                    e.preventDefault()
                    handleSubmit(e)
                  }
                }}
              />
              
              <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-500">
                  Press {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'} + Enter to send
                </p>
                
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="submit"
                  disabled={isLoading || !prompt.trim()}
                  className="px-6 py-3 bg-black text-white rounded-xl hover:bg-gray-800 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 font-medium"
                >
                  {isLoading ? (
                    <>
                      <Zap className="w-4 h-4 animate-spin" />
                      <span>Generating...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      <span>Send Prompt</span>
                    </>
                  )}
                </motion.button>
              </div>
            </div>
          </form>
        </motion.div>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-16 pt-8 border-t border-gray-200"
        >
          <div className="text-center space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-6 text-sm text-gray-600">
              <div className="flex items-center space-x-2">
                <span>Made by</span>
                <a 
                  href="https://eshaam.co.za" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="font-medium text-black hover:text-gray-700 transition-colors flex items-center space-x-1"
                >
                  <span>@eshaam</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
              
              <div className="flex items-center space-x-4">
                <a 
                  href="https://x.com/eshaam" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-black transition-colors flex items-center space-x-1"
                >
                  <Twitter className="w-4 h-4" />
                  <span className="hidden sm:inline">Twitter</span>
                </a>
                
                <a 
                  href="https://www.linkedin.com/in/eshaam/?originalSubdomain=za" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-500 hover:text-black transition-colors flex items-center space-x-1"
                >
                  <Linkedin className="w-4 h-4" />
                  <span className="hidden sm:inline">LinkedIn</span>
                </a>
              </div>
            </div>
            
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
              <Github className="w-4 h-4" />
              <span>Code on</span>
              <a 
                href="https://github.com/eshaam/self-hosted-budget-ai-api" 
                target="_blank" 
                rel="noopener noreferrer"
                className="font-medium text-black hover:text-gray-700 transition-colors flex items-center space-x-1"
              >
                <span>GitHub</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        </motion.footer>
      </div>
    </div>
  )
}

export default App