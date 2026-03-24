import { BrowserRouter, Routes, Route } from 'react-router-dom'
import MainLayout from './components/Layout/MainLayout'

import QuestionFactory from './pages/Dashboard/QuestionFactory'
import QuestionBank from './pages/Management/QuestionBank'
import KnowledgeBase from './pages/Management/KnowledgeBase'
import PracticePage from './pages/Practice/PracticePage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<QuestionFactory />} />
          <Route path="bank" element={<QuestionBank />} />
          <Route path="knowledge" element={<KnowledgeBase />} />
          <Route path="practice" element={<PracticePage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
