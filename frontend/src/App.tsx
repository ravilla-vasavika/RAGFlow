import { Toaster } from 'react-hot-toast';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { MainPanel } from './components/layout/MainPanel';
import './index.css';

export default function App() {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <MainPanel />
      </div>
      <Toaster position="bottom-right" />
    </div>
  );
}
