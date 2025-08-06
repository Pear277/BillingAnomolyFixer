import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://pwoyyeuwclpgrsecoomo.supabase.co';
const supabaseKey = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3b3l5ZXV3Y2xwZ3JzZWNvb21vIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQwNjAyNTksImV4cCI6MjA2OTYzNjI1OX0.3uFUQY8hzynykja1CGkZk2qQnMPRtqA9iwpkBw4oTw8";
export const supabase = createClient(supabaseUrl, supabaseKey);

