import'./globals.css';import{LanguageProvider}from'@/components/LanguageProvider';import AppHeader from'@/components/AppHeader';
export const metadata={title:'Qarar AI — Enterprise Decision Intelligence',description:'From Evidence to Decision to Action'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="ar" dir="rtl"><head>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet"/>
</head><body><LanguageProvider><AppHeader/>{children}<footer><b>QARAR AI</b><span>Human accountable. AI assisted.</span><small>Core + Knowledge active · Connect authenticated · Automation approval-enforced</small></footer></LanguageProvider></body></html>}
