'use client'
import type { FC } from 'react'
import Editor, { loader } from '@monaco-editor/react'
import React, { useEffect, useMemo, useRef, useState } from 'react'
import Base from '../base'
import cn from '@/utils/classnames'
import { CodeLanguage } from '@/app/components/workflow/nodes/code/types'
import {
  getFilesInLogs,
} from '@/app/components/base/file-uploader/utils'
import { Theme } from '@/types/app'
import useTheme from '@/hooks/use-theme'
import './style.css'
import { noop } from 'lodash-es'
import { basePath } from '@/utils/var'

// load file from local instead of cdn https://github.com/suren-atoyan/monaco-react/issues/482
loader.config({ paths: { vs: `${basePath}/vs` } })

const CODE_EDITOR_LINE_HEIGHT = 18

export type Props = {
  value?: string | object
  placeholder?: React.JSX.Element | string
  onChange?: (value: string) => void
  title?: React.JSX.Element
  language: CodeLanguage
  headerRight?: React.JSX.Element
  readOnly?: boolean
  isJSONStringifyBeauty?: boolean
  height?: number
  isInNode?: boolean
  onMount?: (editor: any, monaco: any) => void
  noWrapper?: boolean
  isExpand?: boolean
  showFileList?: boolean
  onGenerated?: (value: string) => void
  showCodeGenerator?: boolean
  className?: string
  tip?: React.JSX.Element
}

export const languageMap = {
  [CodeLanguage.javascript]: 'javascript',
  [CodeLanguage.python3]: 'python',
  [CodeLanguage.json]: 'json',
}

const CodeEditor: FC<Props> = ({
  value = '',
  placeholder = '',
  onChange = noop,
  title = '',
  headerRight,
  language,
  readOnly,
  isJSONStringifyBeauty,
  height,
  isInNode,
  onMount,
  noWrapper,
  isExpand,
  showFileList,
  onGenerated,
  showCodeGenerator = false,
  className,
  tip,
}) => {
  const [isFocus, setIsFocus] = React.useState(false)
  const [isMounted, setIsMounted] = React.useState(false)
  const minHeight = height || 200
  const [editorContentHeight, setEditorContentHeight] = useState(56)
  const { theme: appTheme } = useTheme()
  const valueRef = useRef(value)
  useEffect(() => {
    valueRef.current = value
  }, [value])

  const fileList = useMemo(() => {
    if (typeof value === 'object')
      return getFilesInLogs(value)
    return []
  }, [value])

  const editorRef = useRef<any>(null)
  const resizeEditorToContent = () => {
    if (editorRef.current) {
      const contentHeight = editorRef.current.getContentHeight() // Math.max(, minHeight)
      setEditorContentHeight(contentHeight)
    }
  }

  const handleEditorChange = (value: string | undefined) => {
    onChange(value || '')
    setTimeout(() => {
      resizeEditorToContent()
    }, 10)
  }

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor
    resizeEditorToContent()

    editor.onDidFocusEditorText(() => {
      setIsFocus(true)
    })
    editor.onDidBlurEditorText(() => {
      setIsFocus(false)
    })

    monaco.editor.setTheme(appTheme === Theme.light ? 'light' : 'vs-dark') // Fix: sometimes not load the default theme

    onMount?.(editor, monaco)
    setIsMounted(true)
  }

  const outPutValue = (() => {
    if (!isJSONStringifyBeauty)
      return value as string
    try {
      return JSON.stringify(value as object, null, 2)
    }
    catch {
      return value as string
    }
  })()

  const theme = useMemo(() => {
    if (appTheme === Theme.light)
      return 'light'
    return 'vs-dark'
  }, [appTheme])

  const main = (
    <>
      {/* https://www.npmjs.com/package/@monaco-editor/react */}
      <Editor
        // className='min-h-[100%]' // h-full
        // language={language === CodeLanguage.javascript ? 'javascript' : 'python'}
        language={languageMap[language] || 'javascript'}
        theme={isMounted ? theme : 'default-theme'} // sometimes not load the default theme
        value={outPutValue}
        loading={<span className='text-text-primary'>Loading...</span>}
        onChange={handleEditorChange}
        // https://microsoft.github.io/monaco-editor/typedoc/interfaces/editor.IEditorOptions.html
        options={{
          readOnly,
          domReadOnly: true,
          quickSuggestions: false,
          minimap: { enabled: false },
          lineNumbersMinChars: 1, // would change line num width
          wordWrap: 'on', // auto line wrap
          // lineNumbers: (num) => {
          //   return <div>{num}</div>
          // }
          // hide ambiguousCharacters warning
          unicodeHighlight: {
            ambiguousCharacters: false,
          },
        }}
        onMount={handleEditorDidMount}
      />
      {!outPutValue && !isFocus && <div className='pointer-events-none absolute left-[36px] top-0 text-[13px] font-normal leading-[18px] text-gray-300'>{placeholder}</div>}
    </>
  )

  return (
    <div className={cn(isExpand && 'h-full', className)}>
      {noWrapper
        ? <div className='no-wrapper relative' style={{
          height: isExpand ? '100%' : (editorContentHeight) / 2 + CODE_EDITOR_LINE_HEIGHT, // In IDE, the last line can always be in lop line. So there is some blank space in the bottom.
          minHeight: CODE_EDITOR_LINE_HEIGHT,
        }}>
          {main}
        </div>
        : (
          <Base
            className='relative'
            title={title}
            value={outPutValue}
            headerRight={headerRight}
            isFocus={isFocus && !readOnly}
            minHeight={minHeight}
            isInNode={isInNode}
            onGenerated={onGenerated}
            codeLanguages={language}
            fileList={fileList as any}
            showFileList={showFileList}
            showCodeGenerator={showCodeGenerator}
            tip={tip}
          >
            {main}
          </Base>
        )}
    </div>
  )
}
export default React.memo(CodeEditor)
