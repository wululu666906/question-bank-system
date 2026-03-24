import React from 'react';
import { Filter, Download, MoreVertical } from 'lucide-react';

const QuestionBank: React.FC = () => {
  return (
    <div className="card animate-fade-in" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '0.25rem' }}>题库管理</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>管理所有已生成的题目，支持筛选与按要求导出</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn-secondary"><Filter size={18} /> 高级筛选</button>
          <button className="btn-primary"><Download size={18} /> 导出 Excel</button>
        </div>
      </div>
      
      <div style={{ padding: '1.5rem', flex: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
              <th style={{ padding: '1rem', fontWeight: 500 }}>ID / 知识点</th>
              <th style={{ padding: '1rem', fontWeight: 500 }}>题型</th>
              <th style={{ padding: '1rem', fontWeight: 500 }}>难度</th>
              <th style={{ padding: '1rem', fontWeight: 500 }}>题目预览</th>
              <th style={{ padding: '1rem', fontWeight: 500 }}>操作</th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((item) => (
              <tr key={item} style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '1rem' }}>
                  <div style={{ fontWeight: 500 }}>#B100{item}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>合同违约责任</div>
                </td>
                <td style={{ padding: '1rem' }}><span className="badge badge-primary">选择题</span></td>
                <td style={{ padding: '1rem' }}><span className="badge badge-warning">中等</span></td>
                <td style={{ padding: '1rem', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  根据《民法典》规定，当事人一方不履行合同义务或者履行合同义务不符合约定的...
                </td>
                <td style={{ padding: '1rem' }}>
                  <button className="icon-btn"><MoreVertical size={18} /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default QuestionBank;
