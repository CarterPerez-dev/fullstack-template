/**
 * @AngelaMos | 2026
 * Input.tsx
 */

import { type ComponentRef, forwardRef } from 'react'
import type { TextInput as RNTextInput } from 'react-native'
import {
  type GetProps,
  Stack,
  styled,
  Input as TamaguiInput,
  Text,
} from 'tamagui'

const InputFrame = styled(TamaguiInput, {
  name: 'Input',
  height: 44,
  paddingHorizontal: '$3',
  backgroundColor: 'transparent',
  borderWidth: 1,
  borderColor: '$borderDefault',
  borderRadius: '$2',
  fontSize: 14,
  color: '$white',
  placeholderTextColor: '$textMuted',
  outlineWidth: 0,

  focusStyle: {
    borderColor: '$borderStrong',
  },

  variants: {
    error: {
      true: {
        borderColor: '$errorDefault',
        focusStyle: {
          borderColor: '$errorDefault',
        },
      },
    },
  } as const,
})

const InputContainer = styled(Stack, {
  name: 'InputContainer',
  flexDirection: 'column',
  gap: '$2',
})

const Label = styled(Text, {
  name: 'Label',
  fontSize: 12,
  fontWeight: '500',
  color: '$white',
})

const ErrorText = styled(Text, {
  name: 'ErrorText',
  fontSize: 12,
  color: '$errorDefault',
})

type InputFrameProps = GetProps<typeof InputFrame>
type InputRef = ComponentRef<typeof RNTextInput>

interface InputProps extends Omit<InputFrameProps, 'ref' | 'error'> {
  label?: string
  errorMessage?: string
}

export const Input = forwardRef<InputRef, InputProps>(function Input(
  { label, errorMessage, ...props },
  ref
) {
  if (!label && !errorMessage) {
    return <InputFrame ref={ref} error={!!errorMessage} {...props} />
  }

  return (
    <InputContainer>
      {label && <Label>{label}</Label>}
      <InputFrame ref={ref} error={!!errorMessage} {...props} />
      {errorMessage && <ErrorText>{errorMessage}</ErrorText>}
    </InputContainer>
  )
})

export { ErrorText, InputContainer, InputFrame, Label }
