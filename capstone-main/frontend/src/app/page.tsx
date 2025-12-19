import dynamic from 'next/dynamic';

const Chat = dynamic(() => import('./components/Chat'));

export default function Home() {
  return (
    <main className="min-h-screen bg-white">
      <Chat />
    </main>
  );
}