import { useState } from 'react'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import Markdown from 'react-markdown'
import { Button } from "@radix-ui/themes"
import { MagnifyingGlassIcon } from "@radix-ui/react-icons"

import "@radix-ui/themes/styles.css";
import { Form, } from 'radix-ui'

import './App.css'

function App() {
  const [value, setValue] = useState<string>('')
  const [response, setResponse] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleClick = () => {
    setIsLoading(true)
    setResponse('')
    fetchEventSource('http://localhost:8000/chat', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({
          message: value
      }),
      onmessage: (msg) => {
        setResponse(prevResponse => prevResponse + msg.data)
      },
      onerror: (err) => {
        console.log(err)
      },
      onclose: () => {
        console.log("Finished!")
        setIsLoading(false)
      }
    })  
  }
  
  return (
    <>
      <h1>Ask-the-Web</h1>
      <p>Type a question & let the agent answer in real-time.</p>
      {/* <Form.Root>
        <Form.Field name='question'>

        </Form.Field>
      </Form.Root> */}
      <input value={value} onChange={e => setValue(e.target.value)} type='text' />
      <Button onClick={handleClick} disabled={isLoading}>
        <MagnifyingGlassIcon width={18} height={18} />
        Ask
      </Button>
      <div>
        <Markdown>{response}</Markdown>
      </div>
    </>
  )
}

export default App
