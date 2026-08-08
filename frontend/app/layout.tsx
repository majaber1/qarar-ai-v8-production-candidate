import './globals.css';
import {IBM_Plex_Sans_Arabic,Inter} from 'next/font/google';
import {LanguageProvider} from '@/components/LanguageProvider';
import AppHeader from '@/components/AppHeader';

const arabic=IBM_Plex_Sans_Arabic({subsets:['arabic'],weight:['400','500','600','700'],variable:'--font-arabic'});
const latin=Inter({subsets:['latin'],variable:'--font-latin'});

export const metadata={title:'قرار | منصة القرار المؤسسي',description:'حوّل ملفات المشروع وأسئلته إلى قرار واضح، موثّق، وقابل للتنفيذ.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="ar" dir="rtl" className={`${arabic.variable} ${latin.variable}`}><body><LanguageProvider><AppHeader/>{children}<footer><div><b>قرار</b><span>منصة قرار مؤسسية مبنية للسوق العربي.</span></div><small>الإنسان يعتمد القرار، والذكاء الاصطناعي يوضّح الصورة.</small></footer></LanguageProvider></body></html>}
