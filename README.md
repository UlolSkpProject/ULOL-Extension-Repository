# ULOL Extension Repository

ULOL SketchUp Extension 배포용 manifest와 RBZ 파일을 관리하는 저장소입니다.

## 배포 태그 규칙

공통 배포 워크플로우는 태그 이름을 기준으로 `visibility`와 `distribution` 값을 자동 결정합니다.

기본값은 다음과 같습니다.

- `visibility`: `visible`
- `distribution`: `active`

태그 이름에 아래 suffix가 포함되면 해당 값으로 변경됩니다.

| 태그 조건 | 적용 값 |
| --- | --- |
| `-preview` 포함 | `distribution = preview` |
| `-deprecated` 포함 | `distribution = deprecated` |
| `-disabled` 포함 | `distribution = disabled` |
| `-active` 포함 | `distribution = active` |
| `-hidden-` 포함 또는 `-hidden`으로 끝남 | `visibility = hidden` |

예시:

| 태그 예시 | visibility | distribution |
| --- | --- | --- |
| `v1.2.3` | `visible` | `active` |
| `v1.2.3-preview` | `visible` | `preview` |
| `v1.2.3-hidden` | `hidden` | `active` |
| `v1.2.3-preview-hidden` | `hidden` | `preview` |
| `v1.2.3-disabled` | `visible` | `disabled` |

주의: 태그의 버전 문자열은 배포 상태 판정에만 사용됩니다. 실제 extension 버전은 각 extension repo의 Ruby loader 파일에 정의된 `EXTENSION_VERSION` 상수에서 읽어옵니다.
