{ import: st80 }

Object assert: condition
[
    condition ifFalse: [self error: 'assertion failed']
]

{ import: SqueakImage }
{ import: SqueakObject }
{ import: SqueakIO }
{ import: SqueakBitBlt }

{ import: String-paths }

NilObject			:= [  0 ]
FalseObject			:= [  1 ]
TrueObject			:= [  2 ]
SchedulerAssociation		:= [  3 ]
ClassBitmap			:= [  4 ]
ClassInteger			:= [  5 ]
ClassString			:= [  6 ]
ClassArray			:= [  7 ]
ClassFloat			:= [  9 ]
ClassMethodContext		:= [ 10 ]
ClassBlockContext		:= [ 11 ]
ClassPoint			:= [ 12 ]
ClassLargePositiveInteger	:= [ 13 ]
TheDisplay			:= [ 14 ]
ClassMessage			:= [ 15 ]
ClassCompiledMethod		:= [ 16 ]
TheLowSpaceSemaphore		:= [ 17 ]
ClassSemaphore			:= [ 18 ]
ClassCharacter			:= [ 19 ]
SelectorDoesNotUnderstand	:= [ 20 ]
SelectorCannotReturn		:= [ 21 ]
TheInputSemaphore		:= [ 22 ]
SpecialSelectors		:= [ 23 ]
SqueakCharacterTable		:= [ 24 ]
SelectorMustBeBoolean		:= [ 25 ]
ClassByteArray			:= [ 26 ]
ClassProcess			:= [ 27 ]
CompactClasses			:= [ 28 ]
TheTimerSemaphore		:= [ 29 ]
TheInterruptSemaphore		:= [ 30 ]
FloatProto			:= [ 31 ]
SelectorCannotInterpret		:= [ 34 ]
MethodContextProto		:= [ 35 ]
BlockContextProto		:= [ 37 ]
ExternalObjectsArray		:= [ 38 ]
ClassPseudoContext		:= [ 39 ]
ClassTranslatedMethod		:= [ 40 ]
TheFinalizationSemaphore	:= [ 41 ]
ClassLargeNegativeInteger	:= [ 42 ]
ClassExternalAddress		:= [ 43 ]
ClassExternalStructure		:= [ 44 ]
ClassExternalData		:= [ 45 ]
ClassExternalFunction		:= [ 46 ]
ClassExternalLibrary		:= [ 47 ]
SelectorAboutToReturn		:= [ 48 ]

Class_superclass		:= [ 0 ]
Class_mdict			:= [ 1 ]
Class_format			:= [ 2 ]
Class_name			:= [ 6 ]

Association_key			:= [ 0 ]
Association_value		:= [ 1 ]

ProcSched_processLists		:= [ 0 ]
ProcSched_activeProcess		:= [ 1 ]

Process_suspendedContext	:= [ 1 ]
Process_priority		:= [ 2 ]
Process_myList			:= [ 3 ]

Context_sender			:= [  0 ]
Context_instructionPointer	:= [  1 ]
Context_stackPointer		:= [  2 ]
BlockContext_argumentCount	:= [  3 ]	MethodContext_method		:= [  3 ]
BlockContext_initialPC		:= [  4 ]	MethodContext_receiverMap	:= [  4 ]
BlockContext_home		:= [  5 ]	MethodContext_receiver		:= [  5 ]

Context_stackFrameStart		:= [  5 ]
Context_tempFrameStart		:= [  6 ]
Context_smallFrameSize		:= [ 16 ]	"indexable fields"
Context_largeFrameSize		:= [ 56 ]	"indexable fields"

MethodDictionary_array		:= [ 1 ]
MethodDictionary_selectorStart	:= [ 2 ]

Point_x				:= [ 0 ]
Point_y				:= [ 1 ]

Character_value			:= [ 0 ]

Link_nextLink			:= [ 0 ]

LinkedList_firstLink		:= [ 0 ]
LinkedList_lastLink		:= [ 1 ]

Semaphore_excessSignals		:= [ 2 ]

Message_selector		:= [ 0 ]
Message_arguments		:= [ 1 ]
Message_lookupClass		:= [ 2 ]

MethodCacheSize			:= [ 4096 ]
MethodCacheMask			:= [ MethodCacheSize - 1 ]

MaxPrimitiveIndex		:= [ 700 ]

Squeak : Object ( bytecodeTable primitiveTable viPath vmPath lastHash specialObjectsArray nilObj trueObj falseObj
		  currentBytecode activeContext homeContext receiver method instructionPointer stackPointer
		  messageSelector argumentCount receiverClass lkupClass methodClass newMethod primitiveIndex
		  successFlag lastTick nextPollTick nextWakeupTick interruptPending interruptKeycode
		  interruptCheckCounter interruptCheckCounterFeedbackReset interruptChecksEveryNms
		  methodCacheSelector methodCacheClass methodCacheMethod methodCachePrimitive
		  thisSessionID io bitBlt cacheHits cacheMisses )

"
	INITIALISATION
"

FormatTable := [
    (Array new: 16)
	at:  1 put: FormatEmpty;	"    0 no fields"
	at:  2 put: FormatFixed;	"    1 fixed fields only (all containing pointers)"
	at:  3 put: FormatPointers;	"    2 indexable fields only (all containing pointers)"
	at:  4 put: FormatPointers;	"    3 both fixed and indexable fields (all containing pointers)"
	at:  5 put: FormatWeak;		"    4 both fixed and indexable weak fields (all containing pointers)"
	at:  6 put: nil;		"    5 unused"
	at:  7 put: FormatWords;	"    6 indexable word fields only (no pointers)"
	at:  8 put: nil;		"    7 unused"
	at:  9 put: FormatBytes;	" 8-11 indexable byte fields only (no pointers)"
	at: 10 put: FormatBytes;
	at: 11 put: FormatBytes;
	at: 12 put: FormatBytes;
	at: 13 put: FormatMethod;	"12-15 compiled methods"
	at: 14 put: FormatMethod;
	at: 15 put: FormatMethod;
	at: 16 put: FormatMethod;
	yourself
]

Initialisers := [
    #( initEmpty:fromOop:inImage:withMap:
       initPointers:fromOop:inImage:withMap:
       initPointers:fromOop:inImage:withMap:
       initWeak:fromOop:inImage:withMap:
       initWords:fromOop:inImage:withMap:
       initBytes:fromOop:inImage:withMap:
       initMethod:fromOop:inImage:withMap: ) collect: [:s | s asSelector]
]

Squeak interpret: imageName
[
    | image |
    image := SqueakImage open: imageName.
    self := self on: image.
    viPath := imageName realpath.
    vmPath := (Smalltalk argumentAt: 1) realpath dirname, '/'.
    self interpret.
]

Squeak on: image
[
    | map |
    Squeak := self := self new.

    map := Array new: 1 + image maxObjectIndex.
    SqueakObject initialiseHeap: map size.

    'instantiate objects...' putln.

    image oopsDo: [:imobj |
	| format |
	format := image formatOf: imobj.
        map at:  1 + (image indexOf: imobj)
	    put: (format >= 12 ifTrue: [SqueakMethod] ifFalse: [SqueakObject]) new].

    lastHash := image lastHash.
    specialObjectsArray := map at: 1 + (image indexOf: image specialObjectsOop).

    'initialise objects...' putln.

    image oopsDo: [:imobj |
	| format object size |
	format := FormatTable at: 1 + (image formatOf: imobj).
	object := map at: 1 + (image indexOf: imobj).
	size   := image sizeBitsOf: imobj.
	object initClass: (map at: 1 + (image indexOf: (image fetchClassOf: imobj)))
	       hash:      (image hashBitsOf: imobj)
	       format:    format.
	self _perform: (Initialisers at: 1 + format) w: object w: imobj w: image w: map].

    bitBlt := SqueakBitBlt withInterpreter: self getProxy.
    io     := SqueakIO new.

    thisSessionID := io mSecs.

    interruptCheckCounter := 0.
    interruptCheckCounterFeedbackReset := 1000.
    interruptChecksEveryNms := 3.
    nextPollTick := 0.
    nextWakeupTick := 0.
    lastTick := 0.
    interruptKeycode := 2094.	"cmd-."
    interruptPending := false.

    nilObj   := self splObj: NilObject.
    trueObj  := self splObj: TrueObject.
    falseObj := self splObj: FalseObject.

    self initialiseBytecodeTable.
    self initialisePrimitiveTable.
    self initialiseDebugging.

    methodCacheSelector  := Array new: MethodCacheSize.
    methodCacheClass     := Array new: MethodCacheSize.
    methodCacheMethod    := Array new: MethodCacheSize.
    methodCachePrimitive := Array new: MethodCacheSize.

    cacheHits   := 0.
    cacheMisses := 0.

    self loadInitialContext.
    self printCallStack: activeContext.
]

Squeak initEmpty: obj fromOop: imobj inImage: image withMap: map []

Squeak initPointers: obj fromOop: imobj inImage: image withMap: map
[
    | size field |
    size := image sizeBitsOf: imobj.
    obj initFixed: (image fixedFieldsOf: imobj).
    size := size // 4 - 1.
    obj initPointers: size.
    field := imobj + 4.
    0 to: size - 1 do: [:i |
	| ptr |
	ptr := image longAt: field.
	ptr := (image isIntegerObject: ptr) ifTrue: [image intAt: field] ifFalse: [map at: 1 + (image indexOf: ptr)].
	self assert: (ptr isSmallInteger or: [ptr isSqueakObject]).
	obj storePointer: i with: ptr.
	field := field + 4].
]

Squeak initWords: obj fromOop: imobj inImage: image withMap: map
[
    | size |
    size := image sizeBitsOf: imobj.
    size := size / 4 - 1.
    obj initWords: size.
    0 to: size - 1 do: [:i | obj storeWord: i with: (image longAt: imobj + 4 + (4 * i))].
]

Squeak initBytes: obj fromOop: imobj inImage: image withMap: map
[
    | size |
    size := image sizeBitsOf: imobj.
    size := size - 4 - ((image formatOf: imobj) bitAnd: 3).
    obj initBytes: size.
    0 to: size - 1 do: [:i | obj storeByte: i with: (image byteAt: imobj + 4 + i)].
]

Squeak initMethod: obj fromOop: imobj inImage: image withMap: map
[
    | header size field |
    self initBytes: obj fromOop: imobj inImage: image withMap: map.
    header := image longAt: imobj + 4.
    size := 1 "header" + (image literalCountOfHeader: header).
    obj initLiterals: size.
    field := imobj + 4.
    0 to: size - 1 do: [:i |
	| ptr |
	ptr := image longAt: field.
	ptr := (image isIntegerObject: ptr) ifTrue: [image intAt: field] ifFalse: [map at: 1 + (image indexOf: ptr)].
	self assert: (ptr isSmallInteger or: [ptr isSqueakObject]).
	obj storeLiteral: i with: ptr.
	field := field + 4].
]

Squeak initialiseBytecodeTable
[
    bytecodeTable := Array new: 256.
    self table: bytecodeTable from: self bytecodeTable
]

Squeak initialisePrimitiveTable
[
    primitiveTable := Array new: 1 + MaxPrimitiveIndex.
    self table: primitiveTable from: self primitiveTable
]

Squeak table: anArray from: specArray
[
    "SpecArray is an array of either (index selector) or (index1 index2 selector)."
    | contiguous |
    contiguous := 0.
    specArray do: [ :spec |
        (spec at: 1) == contiguous ifFalse: [self error: 'Non-contiguous table entry'].
        spec size = 2
	    ifTrue:
	       [anArray at: ((spec at: 1) + 1) put: (SelectorTable at: (spec at: 2)).
		contiguous := contiguous + 1]
	    ifFalse:
	       [(spec at: 1) to: (spec at: 2) do: [:i | anArray at: (i + 1) put: (SelectorTable at: (spec at: 3))].
		contiguous := contiguous + ((spec at: 2) - (spec at: 1)) + 1]].
]

Squeak loadInitialContext
[
    | proc |
    proc := self processScheduler fetchPointer: ProcSched_activeProcess.
    activeContext := proc fetchPointer: Process_suspendedContext.
    self fetchContextRegisters: activeContext.
]

"
	ACCESSING
"

Squeak argumentCount	[ ^argumentCount ]
Squeak failed		[ ^successFlag not ]
Squeak nilObject	[ ^nilObj ]
Squeak trueObject	[ ^trueObj ]
Squeak falseObject	[ ^falseObj ]

Squeak splObj: offset
[
    ^specialObjectsArray fetchPointer: offset
]

Squeak processScheduler
[
    ^(self splObj: SchedulerAssociation) fetchPointer: Association_value.
]

"
	CONTEXTS
"

Squeak fetchContextRegisters: activeCntx
[
    | home |
    home := (activeCntx instVarAt: MethodContext_method) isSmallInteger
	ifTrue:  [activeCntx instVarAt: BlockContext_home]
	ifFalse: [activeCntx].
    homeContext := home.
    receiver := home instVarAt: MethodContext_receiver.
    method := home instVarAt: MethodContext_method.
    instructionPointer := activeCntx instVarAt: Context_instructionPointer.
    stackPointer := activeCntx instVarAt: Context_stackPointer.
]

Squeak storeContextRegisters: aContext
[
    aContext instVarAt: Context_instructionPointer put: instructionPointer.
    aContext instVarAt: Context_stackPointer       put: stackPointer.
]

"
	...
"

SmallInteger class	[ ^Squeak splObj: ClassInteger ]

Squeak makePointX: x Y: y
[
    | point |
    (point := SqueakObject newFixed: (self splObj: ClassPoint) hash: self newObjectHash size: 2)
	instVarAt: Point_x put: x;
	instVarAt: Point_y put: y.
    ^point
]

Squeak makeString: aString
[
    | string |
    string := SqueakObject newBytes: (self splObj: ClassString) hash: self newObjectHash indexableSize: aString size.
    1 to: string size do: [:i | string storeByte: i - 1 with: (aString at: i) asciiValue].
    ^string
]

Squeak makeLargeInteger: aLargeInteger
[
    | largeInt |
    largeInt := SqueakObject newBytes: (self splObj: ClassLargePositiveInteger) hash: self newObjectHash indexableSize: 4.
    1 to: 4 do: [:i | largeInt storeByte: i - 1 with: (aLargeInteger digitAt: i)].
    ^largeInt
]

Squeak makeFloat: floatValue
[
    | float |
    float := SqueakObject newWords: (self splObj: ClassFloat) hash: self newObjectHash indexableSize: 2.
    float setFloatValue: floatValue.
    ^float
]

Instantiators := [
    #( instantiateEmpty:hash:indexableSize:		"    0 no fields"
       instantiateFixed:hash:indexableSize:		"    1 fixed fields only (all containing pointers)"
       instantiatePointers:hash:indexableSize:		"    2 indexable fields only (all containing pointers)"
       instantiateFixedPointers:hash:indexableSize:	"    3 both fixed and indexable fields (all containing pointers)"
       instantiateWeakPointers:hash:indexableSize:	"    4 both fixed and indexable weak fields (all containing pointers)"
       instantiateIllegal:hash:indexableSize:		"    5 unused"
       instantiateWords:hash:indexableSize:		"    6 indexable word fields only (no pointers)"
       instantiateIllegal:hash:indexableSize:		"    7 unused"
       instantiateBytes:hash:indexableSize:		" 8-11 indexable byte fields only (no pointers)"
       instantiateBytes:hash:indexableSize:
       instantiateBytes:hash:indexableSize:
       instantiateBytes:hash:indexableSize:
       instantiateMethod:hash:indexableSize:		"12-15 compiled methods"
       instantiateMethod:hash:indexableSize:
       instantiateMethod:hash:indexableSize:
       instantiateMethod:hash:indexableSize:
    ) collect: [:s | s asSelector]
]

Squeak instantiateClass: class indexableSize: indexableSize
[
    ^self _perform: (Instantiators at: 1 + class instSpecOfClass)
	  w: class
	  w: self newObjectHash
	  w: indexableSize
]

Squeak instantiateEmpty: type hash: hash indexableSize: size
[
    self error: 'instantiateEmpty: type hash: hash indexableSize: size'.
    ^SqueakObject new: type hash: hash format: FormatEmpty fixedSize: 0 fields: nil
]

Squeak instantiateFixed: type hash: hash indexableSize: size
[
    size := type instSizeOfClass.
    ^SqueakObject new: type hash: hash format: FormatFixed fixedSize: size fields: (Array new: size withAll: nilObj)
]

Squeak instantiatePointers: type hash: hash indexableSize: size
[
    ^SqueakObject new: type hash: hash format: FormatPointers fixedSize: 0 fields: (Array new: size withAll: nilObj)
]

Squeak instantiateFixedPointers: type hash: hash indexableSize: size
[
    | fixedSize |
    self error: 'instantiateFixedPointers: type hash: hash indexableSize: size'.
    fixedSize := type instSizeOfClass.
    size := fixedSize + size.
    ^SqueakObject new: type hash: hash format: FormatPointers fixedSize: fixedSize fields: (Array new: size withAll: nilObj)
]

WeakArray : Array ()

Squeak instantiateWeak: type hash: hash indexableSize: size
[
    | fixedSize |
    self error: 'instantiateWeak: type hash: hash indexableSize: size'.
    fixedSize := type instSizeOfClass.	"always 0?"
    size += fixedSize + size.
    ^SqueakObject new: type hash: hash format: FormatWeak fixedSize: fixedSize fields: (WeakArray new: size defaultElement: nilObj)
]

Squeak instantiateWords: type hash: hash indexableSize: size
[
    ^SqueakObject new: type hash: hash format: FormatWords fixedSize: 0 fields: (WordArray new: size withAll: 0)
]

Squeak instantiateBytes: type hash: hash indexableSize: size
[
    ^SqueakObject new: type hash: hash format: FormatBytes fixedSize: 0 fields: (ByteArray new: size withAll: 0)
]

Squeak instantiateMethod: type hash: hash indexableSize: size
[
    self error: 'instantiateMethod: type hash: hash indexableSize: size'.
    ^SqueakMethod new: type hash: hash format: FormatMethod fixedSize: 0 fields: (ByteArray new: size withAll: 0)
]

{ import: Squeak-machine }
{ import: Squeak-bytecodes }
{ import: Squeak-primitives }
{ import: Squeak-debug }

{ import: SqueakProxy }

Squeak error: excuse
[
    $\n put.
    self printCallStack: activeContext.
    $\n put.
    super error: excuse
]

Object error: reason
[
    $\n put.
    Squeak printCallStack.
    reason putln.
    { abort(); }.
]

