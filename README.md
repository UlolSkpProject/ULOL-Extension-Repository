# ULOL Extension Repository

ULOL SketchUp Extension 배포용 manifest와 RBZ 파일을 관리하는 저장소입니다.

## RBZ 패키지 규칙

온라인과 오프라인 배포에는 동일한 `.rbz` 파일을 사용합니다. 공통 배포 워크플로는 RBZ 루트에 `seoul_space_package.json`을 자동 생성하며, 다음 항목을 기록합니다.

- `schema_version`
- `id`
- `name`
- `version`
- `loader`
- `source_dir`
- `description`
- `category`

온라인 설치는 `manifest.json`만 사용하고 이 내부 파일을 무시합니다. SeoulSpace Extension Manager의 오프라인 설치는 RBZ 내부 파일을 읽어 패키지를 식별하고 검증합니다.

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
