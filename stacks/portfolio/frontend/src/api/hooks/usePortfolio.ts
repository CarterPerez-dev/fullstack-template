// ===================
// © AngelaMos | 2026
// usePortfolio.ts
// ===================

import {
  type UseMutationResult,
  type UseQueryResult,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query'
import { toast } from 'sonner'
import {
  type CertificationInput,
  type CertificationResponse,
  type CustomSectionInput,
  type CustomSectionResponse,
  type ExperienceInput,
  type ExperienceResponse,
  isValidPortfolioResponse,
  isValidRegistrationStatus,
  type LinkInput,
  type LinkResponse,
  type MediaResponse,
  PORTFOLIO_ERROR_MESSAGES,
  PORTFOLIO_SUCCESS_MESSAGES,
  type PortfolioResponse,
  PortfolioResponseError,
  type ProfileResponse,
  type ProfileUpdateRequest,
  type ProjectInput,
  type ProjectResponse,
  type RegistrationStatus,
  type SiteSettingsResponse,
  type SiteSettingsUpdateRequest,
  type SkillGroupInput,
  type SkillGroupResponse,
} from '@/api/types'
import { API_ENDPOINTS, PORTFOLIO_RESOURCES, QUERY_KEYS } from '@/config'
import { apiClient, QUERY_STRATEGIES } from '@/core/api'

const invalidateAll = (
  queryClient: ReturnType<typeof useQueryClient>
): Promise<void> =>
  queryClient.invalidateQueries({ queryKey: QUERY_KEYS.PORTFOLIO.ALL })

export const usePortfolio = (): UseQueryResult<PortfolioResponse, Error> =>
  useQuery({
    queryKey: QUERY_KEYS.PORTFOLIO.PUBLIC(),
    queryFn: async (): Promise<PortfolioResponse> => {
      const response = await apiClient.get<unknown>(
        API_ENDPOINTS.PORTFOLIO.PUBLIC
      )
      if (!isValidPortfolioResponse(response.data)) {
        throw new PortfolioResponseError(
          PORTFOLIO_ERROR_MESSAGES.INVALID_RESPONSE,
          API_ENDPOINTS.PORTFOLIO.PUBLIC
        )
      }
      return response.data
    },
    ...QUERY_STRATEGIES.standard,
  })

export const useRegistrationStatus = (): UseQueryResult<
  RegistrationStatus,
  Error
> =>
  useQuery({
    queryKey: QUERY_KEYS.PORTFOLIO.REGISTRATION(),
    queryFn: async (): Promise<RegistrationStatus> => {
      const response = await apiClient.get<unknown>(
        API_ENDPOINTS.PORTFOLIO.REGISTRATION_STATUS
      )
      if (!isValidRegistrationStatus(response.data)) {
        throw new PortfolioResponseError(
          PORTFOLIO_ERROR_MESSAGES.INVALID_RESPONSE,
          API_ENDPOINTS.PORTFOLIO.REGISTRATION_STATUS
        )
      }
      return response.data
    },
    ...QUERY_STRATEGIES.standard,
  })

export const useUpdatePortfolioProfile = (): UseMutationResult<
  ProfileResponse,
  Error,
  ProfileUpdateRequest
> => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (data: ProfileUpdateRequest): Promise<ProfileResponse> => {
      const response = await apiClient.patch<ProfileResponse>(
        API_ENDPOINTS.PORTFOLIO.PROFILE,
        data
      )
      return response.data
    },
    onSuccess: async (): Promise<void> => {
      await invalidateAll(queryClient)
      toast.success(PORTFOLIO_SUCCESS_MESSAGES.SAVED)
    },
    onError: (): void => {
      toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_SAVE)
    },
  })
}

export const useUpdateSettings = (): UseMutationResult<
  SiteSettingsResponse,
  Error,
  SiteSettingsUpdateRequest
> => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (
      data: SiteSettingsUpdateRequest
    ): Promise<SiteSettingsResponse> => {
      const response = await apiClient.patch<SiteSettingsResponse>(
        API_ENDPOINTS.PORTFOLIO.SETTINGS,
        data
      )
      return response.data
    },
    onSuccess: async (): Promise<void> => {
      await invalidateAll(queryClient)
      toast.success(PORTFOLIO_SUCCESS_MESSAGES.SAVED)
    },
    onError: (): void => {
      toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_SAVE)
    },
  })
}

interface UpdateVars<TInput> {
  id: string
  data: TInput
}

interface ResourceHooks<TResponse, TInput> {
  useList: () => UseQueryResult<TResponse[], Error>
  useCreate: () => UseMutationResult<TResponse, Error, TInput>
  useUpdate: () => UseMutationResult<TResponse, Error, UpdateVars<TInput>>
  useDelete: () => UseMutationResult<void, Error, string>
  useReorder: () => UseMutationResult<void, Error, string[]>
}

function createResourceHooks<TResponse, TInput>(
  resource: string
): ResourceHooks<TResponse, TInput> {
  const listKey = (): readonly unknown[] =>
    QUERY_KEYS.PORTFOLIO.RESOURCE(resource)

  const useList = (): UseQueryResult<TResponse[], Error> =>
    useQuery({
      queryKey: listKey(),
      queryFn: async (): Promise<TResponse[]> => {
        const response = await apiClient.get<TResponse[]>(
          API_ENDPOINTS.PORTFOLIO.RESOURCE(resource)
        )
        return response.data
      },
      ...QUERY_STRATEGIES.standard,
    })

  const useCreate = (): UseMutationResult<TResponse, Error, TInput> => {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: async (data: TInput): Promise<TResponse> => {
        const response = await apiClient.post<TResponse>(
          API_ENDPOINTS.PORTFOLIO.RESOURCE(resource),
          data
        )
        return response.data
      },
      onSuccess: async (): Promise<void> => {
        await invalidateAll(queryClient)
        toast.success(PORTFOLIO_SUCCESS_MESSAGES.CREATED)
      },
      onError: (): void => {
        toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_SAVE)
      },
    })
  }

  const useUpdate = (): UseMutationResult<
    TResponse,
    Error,
    UpdateVars<TInput>
  > => {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: async (vars: UpdateVars<TInput>): Promise<TResponse> => {
        const response = await apiClient.patch<TResponse>(
          API_ENDPOINTS.PORTFOLIO.RESOURCE_ITEM(resource, vars.id),
          vars.data
        )
        return response.data
      },
      onSuccess: async (): Promise<void> => {
        await invalidateAll(queryClient)
        toast.success(PORTFOLIO_SUCCESS_MESSAGES.SAVED)
      },
      onError: (): void => {
        toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_SAVE)
      },
    })
  }

  const useDelete = (): UseMutationResult<void, Error, string> => {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: async (id: string): Promise<void> => {
        await apiClient.delete(
          API_ENDPOINTS.PORTFOLIO.RESOURCE_ITEM(resource, id)
        )
      },
      onSuccess: async (): Promise<void> => {
        await invalidateAll(queryClient)
        toast.success(PORTFOLIO_SUCCESS_MESSAGES.DELETED)
      },
      onError: (): void => {
        toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_DELETE)
      },
    })
  }

  const useReorder = (): UseMutationResult<void, Error, string[]> => {
    const queryClient = useQueryClient()
    return useMutation({
      mutationFn: async (orderedIds: string[]): Promise<void> => {
        await apiClient.post(API_ENDPOINTS.PORTFOLIO.RESOURCE_REORDER(resource), {
          ordered_ids: orderedIds,
        })
      },
      onSuccess: async (): Promise<void> => {
        await invalidateAll(queryClient)
      },
      onError: (): void => {
        toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_REORDER)
      },
    })
  }

  return { useList, useCreate, useUpdate, useDelete, useReorder }
}

const certifications = createResourceHooks<
  CertificationResponse,
  CertificationInput
>(PORTFOLIO_RESOURCES.CERTIFICATIONS)
export const useCertifications = certifications.useList
export const useCreateCertification = certifications.useCreate
export const useUpdateCertification = certifications.useUpdate
export const useDeleteCertification = certifications.useDelete
export const useReorderCertifications = certifications.useReorder

const projects = createResourceHooks<ProjectResponse, ProjectInput>(
  PORTFOLIO_RESOURCES.PROJECTS
)
export const useProjects = projects.useList
export const useCreateProject = projects.useCreate
export const useUpdateProject = projects.useUpdate
export const useDeleteProject = projects.useDelete
export const useReorderProjects = projects.useReorder

const experience = createResourceHooks<ExperienceResponse, ExperienceInput>(
  PORTFOLIO_RESOURCES.EXPERIENCE
)
export const useExperience = experience.useList
export const useCreateExperience = experience.useCreate
export const useUpdateExperience = experience.useUpdate
export const useDeleteExperience = experience.useDelete
export const useReorderExperience = experience.useReorder

const skillGroups = createResourceHooks<SkillGroupResponse, SkillGroupInput>(
  PORTFOLIO_RESOURCES.SKILL_GROUPS
)
export const useSkillGroups = skillGroups.useList
export const useCreateSkillGroup = skillGroups.useCreate
export const useUpdateSkillGroup = skillGroups.useUpdate
export const useDeleteSkillGroup = skillGroups.useDelete
export const useReorderSkillGroups = skillGroups.useReorder

const links = createResourceHooks<LinkResponse, LinkInput>(
  PORTFOLIO_RESOURCES.LINKS
)
export const useLinks = links.useList
export const useCreateLink = links.useCreate
export const useUpdateLink = links.useUpdate
export const useDeleteLink = links.useDelete
export const useReorderLinks = links.useReorder

const customSections = createResourceHooks<
  CustomSectionResponse,
  CustomSectionInput
>(PORTFOLIO_RESOURCES.CUSTOM_SECTIONS)
export const useCustomSections = customSections.useList
export const useCreateCustomSection = customSections.useCreate
export const useUpdateCustomSection = customSections.useUpdate
export const useDeleteCustomSection = customSections.useDelete
export const useReorderCustomSections = customSections.useReorder

export const useMediaList = (): UseQueryResult<MediaResponse[], Error> =>
  useQuery({
    queryKey: QUERY_KEYS.PORTFOLIO.MEDIA(),
    queryFn: async (): Promise<MediaResponse[]> => {
      const response = await apiClient.get<MediaResponse[]>(
        API_ENDPOINTS.PORTFOLIO.MEDIA
      )
      return response.data
    },
    ...QUERY_STRATEGIES.standard,
  })

export const useUploadMedia = (): UseMutationResult<
  MediaResponse,
  Error,
  File
> => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (file: File): Promise<MediaResponse> => {
      const formData = new FormData()
      formData.append('file', file)
      const response = await apiClient.post<MediaResponse>(
        API_ENDPOINTS.PORTFOLIO.MEDIA,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return response.data
    },
    onSuccess: async (): Promise<void> => {
      await queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.PORTFOLIO.MEDIA(),
      })
      toast.success(PORTFOLIO_SUCCESS_MESSAGES.UPLOADED)
    },
    onError: (): void => {
      toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_UPLOAD)
    },
  })
}

export const useDeleteMedia = (): UseMutationResult<void, Error, string> => {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await apiClient.delete(API_ENDPOINTS.PORTFOLIO.MEDIA_ITEM(id))
    },
    onSuccess: async (): Promise<void> => {
      await invalidateAll(queryClient)
      toast.success(PORTFOLIO_SUCCESS_MESSAGES.DELETED)
    },
    onError: (): void => {
      toast.error(PORTFOLIO_ERROR_MESSAGES.FAILED_TO_DELETE)
    },
  })
}
