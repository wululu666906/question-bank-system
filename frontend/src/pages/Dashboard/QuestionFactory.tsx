import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, FileText, CheckCircle, Database } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { triggerQuestionGeneration, formatDifyParams } from '../../services/difyClient';
import type { QuestionType, Difficulty, GeneratedQuestion } from '../../services/difyClient';
import './QuestionFactory.css';

// 极简错误边界，防止渲染崩溃导致白屏
class RenderErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean}> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError) {
      return (
        <div className="card" style={{ padding: '2rem', textAlign: 'center', backgroundColor: 'rgba(254, 242, 242, 0.8)', border: '1px solid #FECACA', borderRadius: '12px' }}>
          <h3 style={{ color: '#DC2626', fontWeight: 'bold', marginBottom: '1rem' }}>预览渲染出现异常</h3>
          <p style={{ color: '#4B5563', fontSize: '0.9rem', lineHeight: '1.6' }}>
            AI 生成的内容中可能包含了无法解析的特殊字符或格式，导致渲染引擎崩溃。
            这通常是因为外部搜索抓取到的内容过于复杂。
          </p>
          <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center' }}>
            <button className="btn-primary" onClick={() => window.location.reload()}>刷新界面</button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const QuestionFactory: React.FC = () => {
  // Form State
  const [content, setContent] = useState('');
  const [selectedTypes, setSelectedTypes] = useState<QuestionType[]>(['choice']);
  const [difficulty, setDifficulty] = useState<Difficulty>('medium');
  const [count, setCount] = useState<number>(3);
  const [jobDirection, setJobDirection] = useState('');

  const [isGenerating, setIsGenerating] = useState(false);
  const [progressMsg, setProgressMsg] = useState('AI 引擎生成中...');
  const [results, setResults] = useState<GeneratedQuestion[]>([]);
  const [streamedText, setStreamedText] = useState('');
  const [fallbackText, setFallbackText] = useState('');
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (isGenerating && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [streamedText, isGenerating]);

  const renderMarkdown = (text: string) => {
    const parts = (text || '').split(/(<think>[\s\S]*?<\/think>)/g);
    return parts.map((part, i) => {
      if (part.startsWith('<think>')) {
        const content = part.replace(/<\/?think>/g, '').trim();
        return content ? (
          <div key={i} className="thought-block animate-fade-in">
            {content}
          </div>
        ) : null;
      }
      return (
        <ReactMarkdown 
          key={i}
          remarkPlugins={[remarkMath]} 
          rehypePlugins={[rehypeKatex]}
        >
          {part.replace(/\\\(([\s\S]*?)\\\)/g, '$$$1$$').replace(/\\\[([\s\S]*?)\\\]/g, '$$$$$1$$$$')}
        </ReactMarkdown>
      );
    });
  };

  const toggleType = (type: QuestionType) => {
    setSelectedTypes(prev => 
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const handleGenerate = async () => {
    if (!content.trim()) return alert('请输入知识点内容');
    if (selectedTypes.length === 0) return alert('请至少选择一种题型');
    if (count < 1) return alert('请设置有效的生成数量');
    
    setIsGenerating(true);
    setProgressMsg('AI 引擎初始化...');
    setResults([]);
    setStreamedText('');
    setFallbackText('');

    try {
      const params = formatDifyParams(content, selectedTypes, difficulty, count, jobDirection);
      const output = await triggerQuestionGeneration(params, (msg) => {
         setProgressMsg(msg);
      }, (chunk) => {
         setStreamedText(prev => prev + chunk);
      });
      console.log('[QuestionFactory] 最终输出:', output);
      setResults(output.parsed);
      if (output.parsed.length === 0 && output.raw) {
         setFallbackText(output.raw);
      }
    } catch (error: any) {
      alert(`报错：${error.message || '未知错误'}`);
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="factory-container animate-fade-in">
      {/* Left Column: Form Setup */}
      <div className="config-panel card">
        <div className="panel-header">
          <h2 className="panel-title">题库智能生产</h2>
          <p className="panel-desc">输入原始素材，AI自动分析并结构化产出高质量题库</p>
        </div>

        <div className="form-group">
          <label className="form-label">
            原始素材 / 知识内容 <span className="required">*</span>
          </label>
          <textarea 
            className="content-textarea" 
            placeholder="在此粘贴法规、案例、内部规定或培训资料汇编..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>

        <div className="form-group split-group">
          <div>
            <label className="form-label">岗位/职业</label>
            <input 
              type="text" 
              className="text-input" 
              placeholder="例如：法务、销售、人力资源"
              value={jobDirection}
              onChange={(e) => setJobDirection(e.target.value)}
            />
          </div>
          <div>
            <label className="form-label">生成数量</label>
            <input 
              type="number" 
              className="text-input" 
              min="1" max="20"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value))}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">生成难度</label>
          <div className="toggle-group">
            <button className={`toggle-btn ${difficulty === 'easy' ? 'active easy' : ''}`} onClick={() => setDifficulty('easy')}>简单</button>
            <button className={`toggle-btn ${difficulty === 'medium' ? 'active medium' : ''}`} onClick={() => setDifficulty('medium')}>中等</button>
            <button className={`toggle-btn ${difficulty === 'hard' ? 'active hard' : ''}`} onClick={() => setDifficulty('hard')}>困难</button>
            <button className={`toggle-btn ${difficulty === 'expert' ? 'active expert' : ''}`} onClick={() => setDifficulty('expert')}>专家级</button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">题型设置</label>
          <div className="toggle-group">
            <button 
              className={`toggle-btn ${selectedTypes.includes('choice') ? 'active' : ''}`} 
              onClick={() => toggleType('choice')}
            >单选题</button>
            <button 
              className={`toggle-btn ${selectedTypes.includes('multiple') ? 'active' : ''}`} 
              onClick={() => toggleType('multiple')}
            >多选题</button>
            <button 
              className={`toggle-btn ${selectedTypes.includes('boolean') ? 'active' : ''}`} 
              onClick={() => toggleType('boolean')}
            >判断题</button>
            <button 
              className={`toggle-btn ${selectedTypes.includes('subjective') ? 'active' : ''}`} 
              onClick={() => toggleType('subjective')}
            >主观题</button>
            <button 
              className={`toggle-btn ${selectedTypes.includes('material') ? 'active' : ''}`} 
              onClick={() => toggleType('material')}
            >材料题</button>
            <button 
              className={`toggle-btn ${selectedTypes.includes('essay') ? 'active' : ''}`} 
              onClick={() => toggleType('essay')}
            >作文</button>
          </div>
        </div>

        <div className="action-footer">
          <button className="btn-primary w-full shadow-lg" onClick={handleGenerate} disabled={isGenerating}>
            {isGenerating ? (
              <><Sparkles className="spin" size={20} /> {progressMsg}</>
            ) : (
              <><Sparkles size={20} /> 智能一键出题</>
            )}
          </button>
        </div>
      </div>

      {/* Right Column: Preview Area */}
      <div className="preview-panel">
        <RenderErrorBoundary>
          <div className="preview-header">
          <h3 className="preview-title">生成结果预览展板</h3>
          {results.length > 0 && (
             <button className="btn-secondary">
               <Database size={16} /> 一键入库
             </button>
          )}
        </div>
        
        <div className="preview-content" ref={scrollRef}>
          {!isGenerating && results.length === 0 && !fallbackText && (
            <div className="empty-state">
              <FileText size={48} className="empty-icon" />
              <p>左侧配置参数后点击生成，在此处预览生成的题目集</p>
            </div>
          )}

          {/* 1. 生成中：展示流式 Markdown */}
          {isGenerating && streamedText && (
            <div className="streaming-container card animate-fade-in" style={{ padding: '1.5rem', marginBottom: '1rem', lineHeight: 1.6 }}>
              <div style={{color: 'var(--primary-color)', fontWeight: 'bold', marginBottom: '1rem'}}>
                {progressMsg} <span className="blink-cursor"></span>
              </div>
              <div className="markdown-body" style={{ fontSize: '0.95rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap'}}>
                {renderMarkdown(streamedText)}
              </div>
            </div>
          )}

          {/* 2. 生成后：显示完整 Markdown（ChatGPT 风格） */}
          {!isGenerating && (streamedText || fallbackText) && (
            <div className="streaming-container card animate-fade-in" style={{ padding: '1.5rem', marginBottom: '1rem', lineHeight: 1.6 }}>
               <h3 style={{ color: 'var(--success-color)', marginBottom: '1rem' }}><CheckCircle size={20} style={{verticalAlign:'middle', marginRight:'8px'}}/> AI 题库生成完毕</h3>
               <div className="markdown-body" style={{ fontSize: '0.95rem', color: 'var(--text-primary)', whiteSpace: 'pre-wrap'}}>
                 {renderMarkdown(streamedText || fallbackText)}
               </div>
            </div>
          )}

          {/* 3. 生成中：尚未开始流式传输时的骨架屏 */}
          {isGenerating && !streamedText && (
            <div className="loading-state">
              <div style={{textAlign: 'center', marginBottom: '1rem', color: 'var(--text-muted)'}}>{progressMsg}</div>
              {[...Array(3)].map((_, i) => (
                <div key={i} className="skeleton-card card">
                  <div className="skeleton title-sk" />
                  <div className="skeleton line-sk" />
                  <div className="skeleton line-sk" style={{ width: '80%' }} />
                </div>
              ))}
            </div>
          )}

          {/* 4. 这种模式下不直接展示题目卡片，而是提供交互入口或在 Markdown 中自然展开。
              用户已要求“不折叠成图片那样”，所以我们主要以 Markdown 形式展示。 
              如果后续需要查看列表化结果，可以在此处添加一个切换开关。 */}
        </div>
        </RenderErrorBoundary>
      </div>
    </div>
  );
};

export default QuestionFactory;
