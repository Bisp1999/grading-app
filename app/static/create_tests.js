(function () {
  'use strict';

  function getContext() {
    return (window.CREATE_TESTS_CONTEXT || {});
  }

  // Store classrooms data for dynamic updates
  function getClassroomsByGrade() {
    return getContext().classroomsByGrade || {};
  }

  function getTeacherType() {
    return getContext().teacherType || '';
  }

  // Update grade dropdown when class is selected (for form)
  function updateGradeFromClassForm() {
    if (getTeacherType() !== 'specialist') return;

    const classSelect = document.getElementById('class_name');
    const gradeSelect = document.getElementById('grade');
    if (!classSelect || !gradeSelect) return;

    const selectedClass = classSelect.value;

    if (selectedClass) {
      const selectedOption = classSelect.options[classSelect.selectedIndex];
      const grade = selectedOption ? selectedOption.getAttribute('data-grade') : null;

      if (grade) {
        gradeSelect.value = grade;
      }
    }
  }

  // Update class options based on selected grade (for form)
  function updateClassOptions() {
    const gradeSelect = document.getElementById('grade');
    const classSelect = document.getElementById('class_name');
    if (!gradeSelect || !classSelect) return;

    const selectedGrade = gradeSelect.value;
    const classroomsByGrade = getClassroomsByGrade();

    classSelect.innerHTML = '<option value="">Select Class</option>';

    if (selectedGrade && classroomsByGrade[selectedGrade]) {
      classroomsByGrade[selectedGrade].forEach((className) => {
        const option = document.createElement('option');
        option.value = className;
        option.textContent = className;
        classSelect.appendChild(option);
      });
    }
  }

  // Update grade dropdown when class is selected (for filter)
  function updateGradeFromClass() {
    if (getTeacherType() !== 'specialist') return;

    const classSelect = document.getElementById('filter_class');
    const gradeSelect = document.getElementById('filter_grade');
    if (!classSelect || !gradeSelect) return;

    const selectedClass = classSelect.value;

    if (selectedClass) {
      const selectedOption = classSelect.options[classSelect.selectedIndex];
      const grade = selectedOption ? selectedOption.getAttribute('data-grade') : null;

      if (grade) {
        gradeSelect.value = grade;
      }
    }
  }

  // Update filter class options based on selected grade (for filter)
  function updateFilterClassOptions() {
    const gradeSelect = document.getElementById('filter_grade');
    const classSelect = document.getElementById('filter_class');

    if (!gradeSelect || !classSelect) {
      console.log('Filter elements not found, skipping updateFilterClassOptions');
      return;
    }

    const selectedGrade = gradeSelect.value;
    const currentSelectedClass = classSelect.value;
    const classroomsByGrade = getClassroomsByGrade();

    classSelect.innerHTML = '<option value="">All Classes</option>';

    if (selectedGrade && classroomsByGrade[selectedGrade]) {
      classroomsByGrade[selectedGrade].forEach((className) => {
        const option = document.createElement('option');
        option.value = className;
        option.textContent = className;
        classSelect.appendChild(option);
      });
    } else {
      Object.keys(classroomsByGrade).forEach((grade) => {
        classroomsByGrade[grade].forEach((className) => {
          const option = document.createElement('option');
          option.value = className;
          option.textContent = `${className} (${grade})`;
          option.setAttribute('data-grade', grade);
          classSelect.appendChild(option);
        });
      });
    }

    if (currentSelectedClass) {
      const optionExists = Array.from(classSelect.options).some((option) => option.value === currentSelectedClass);
      if (optionExists) {
        classSelect.value = currentSelectedClass;
      }
    }
  }

  // Filter tests based on selected criteria
  function filterTests() {
    const globalClassFilter = document.getElementById('global_class_filter');
    const globalSemesterFilter = document.getElementById('global_semester_filter');
    const subjectFilter = document.getElementById('filter_subject');

    const teacherType = getTeacherType();

    const className = globalClassFilter ? globalClassFilter.value : '';
    const semester = globalSemesterFilter ? globalSemesterFilter.value : '';
    const subject = teacherType === 'homeroom' && subjectFilter ? subjectFilter.value : '';

    const rows = document.querySelectorAll('.test-row');

    rows.forEach((row) => {
      let show = true;

      if (semester && row.dataset.semester !== semester) show = false;
      if (className && row.dataset.class !== className) show = false;
      if (subject && row.dataset.subject !== subject) show = false;

      row.style.display = show ? '' : 'none';
    });

    updateFilterDisplay();
    calculateTotals();
    checkCreateTestsButtonState();
  }

  // Update the filter display text (kept for compatibility)
  function updateFilterDisplay() {}

  // Calculate totals for each competency column
  function calculateTotals() {
    const competencies = getContext().competencies || [];

    competencies.forEach((competency) => {
      let total = 0;
      const visibleRows = document.querySelectorAll('.test-row:not([style*="display: none"])');

      visibleRows.forEach((row) => {
        const cell = row.querySelector(`.competency-cell[data-competency="${competency}"]`);
        if (cell && cell.textContent.trim()) {
          const weight = parseFloat(cell.textContent.replace('%', ''));
          if (!Number.isNaN(weight)) {
            total += weight;
          }
        }
      });

      const totalCell = document.querySelector(`#totalsRow [data-competency="${competency}"]`);
      if (totalCell) {
        totalCell.textContent = total + '%';
      }
    });
  }

  // Edit test function
  function editTest(testId) {
    console.log('Edit button clicked for test ID:', testId);
    fetch(`/api/get_test/${testId}`)
      .then((response) => {
        console.log('API response status:', response.status);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then((test) => {
        console.log('Test data received:', test);

        if (test.error) {
          throw new Error(test.error);
        }

        try {
          document.getElementById('semester').value = test.semester;
          document.getElementById('test_name').value = test.test_name;
          document.getElementById('max_points').value = test.max_points;
          document.getElementById('test_date').value = test.test_date;
          document.getElementById('test_weight').value = test.test_weight;
          document.getElementById('competency').value = test.competency;

          const teacherType = getTeacherType();

          if (teacherType === 'specialist') {
            document.getElementById('grade').value = test.grade;
            updateClassOptions();
            setTimeout(() => {
              const classSelect = document.getElementById('class_name');
              if (classSelect && test.class_name) {
                classSelect.value = test.class_name;
              }
            }, 100);
          } else {
            const subjectSelect = document.getElementById('subject');
            if (subjectSelect && test.subject) {
              subjectSelect.value = test.subject;
            }
          }

          document.getElementById('editTestId').value = testId;
          document.getElementById('submitButton').textContent = 'Update Test';
          document.getElementById('deleteButton').style.display = 'block';

          const scopeSelect = document.getElementById('test_scope');
          if (scopeSelect) {
            scopeSelect.value = 'class_only';
            scopeSelect.disabled = true;
          }

          const defineTestsCard = document.getElementById('defineTestsCard');
          const createTestsBtn = document.getElementById('createTestsBtn');

          if (defineTestsCard) {
            if (defineTestsCard.style.display === 'none' || defineTestsCard.style.display === '') {
              defineTestsCard.style.display = 'block';
              if (createTestsBtn) {
                const translations = getContext().translations || {};
                createTestsBtn.innerHTML =
                  '<i class="fas fa-eye-slash me-1"></i>' + (translations.hideForm || 'Hide Form');
              }
            }
            defineTestsCard.scrollIntoView({ behavior: 'smooth' });
          } else {
            console.warn('defineTestsCard element not found, cannot scroll');
          }

          console.log('Test data successfully loaded into form');
        } catch (formError) {
          console.error('Error populating form fields:', formError);
        }
      })
      .catch((error) => {
        console.error('Error loading test:', error);
        alert('Error loading test data: ' + error.message);
      });
  }

  // Confirm delete test
  function confirmDeleteTest() {
    if (
      confirm(
        'Warning: Deleting this test will also delete any grades that have been entered for this test. Are you sure you want to proceed?'
      )
    ) {
      const testId = document.getElementById('editTestId').value;

      fetch(`/api/delete_test/${testId}`, {
        method: 'DELETE',
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            location.reload();
          } else {
            alert('Error deleting test: ' + data.error);
          }
        })
        .catch((error) => {
          console.error('Error deleting test:', error);
          alert('Error deleting test');
        });
    }
  }

  // Reset form to create mode
  function resetForm() {
    document.getElementById('editTestId').value = '';
    document.getElementById('submitButton').textContent = 'Create Test';
    document.getElementById('deleteButton').style.display = 'none';

    const scopeSelect = document.getElementById('test_scope');
    if (scopeSelect) {
      scopeSelect.value = 'grade_all';
      scopeSelect.disabled = false;
    }
  }

  // Function to check if Class and Semester are selected and update Create Tests button
  function checkCreateTestsButtonState() {
    const globalClassFilter = document.getElementById('global_class_filter');
    const globalSemesterFilter = document.getElementById('global_semester_filter');
    const createTestsBtn = document.getElementById('createTestsBtn');

    const teacherType = getTeacherType();

    let classSelected = false;
    let semesterSelected = false;

    if (teacherType === 'specialist') {
      classSelected = !!(globalClassFilter && globalClassFilter.value !== '');
    } else {
      classSelected = true;
    }

    semesterSelected = !!(globalSemesterFilter && globalSemesterFilter.value !== '');

    const shouldEnable = classSelected && semesterSelected;

    if (createTestsBtn) {
      createTestsBtn.disabled = !shouldEnable;
    }

    const testsTable = document.getElementById('testsTable');
    const noSelectionMessage = document.getElementById('noSelectionMessage');

    if (shouldEnable) {
      if (testsTable) testsTable.style.display = 'block';
      if (noSelectionMessage) noSelectionMessage.style.display = 'none';
    } else {
      if (testsTable) testsTable.style.display = 'none';
      if (noSelectionMessage) noSelectionMessage.style.display = 'block';
    }

    updateDefineTestsDisplay();
  }

  // Function to update the display values in Define Tests form
  function updateDefineTestsDisplay() {
    const globalClassFilter = document.getElementById('global_class_filter');
    const globalSemesterFilter = document.getElementById('global_semester_filter');

    const headerInfo = document.getElementById('header_class_semester_info');

    const hiddenClass = document.getElementById('class_name');
    const hiddenSemester = document.getElementById('semester');
    const hiddenGrade = document.getElementById('grade');

    const teacherType = getTeacherType();

    if (teacherType === 'specialist') {
      if (globalClassFilter && globalClassFilter.value !== '') {
        const selectedOption = globalClassFilter.options[globalClassFilter.selectedIndex];
        const displayText = selectedOption ? selectedOption.textContent : '';
        if (hiddenClass) hiddenClass.value = globalClassFilter.value;

        let grade = selectedOption ? selectedOption.getAttribute('data-grade') : null;
        if (!grade) {
          const match = (displayText || '').match(/\(([^)]+)\)\s*$/);
          if (match && match[1]) {
            grade = match[1];
          }
        }
        if (grade && hiddenGrade) {
          hiddenGrade.value = grade;
        }

        if (headerInfo && globalSemesterFilter && globalSemesterFilter.value !== '') {
          headerInfo.textContent = `CLASS: ${displayText} - SEMESTER: ${globalSemesterFilter.value}`;
        } else if (headerInfo) {
          headerInfo.textContent = '';
        }
      } else {
        if (hiddenClass) hiddenClass.value = '';
        if (hiddenGrade) hiddenGrade.value = '';
        if (headerInfo) headerInfo.textContent = '';
      }
    } else {
      const ctx = getContext();
      if (hiddenClass) hiddenClass.value = ctx.homeroomClassName || '';
      if (hiddenGrade) hiddenGrade.value = ctx.homeroomGrade || '';

      if (headerInfo && globalSemesterFilter && globalSemesterFilter.value !== '') {
        const className = ctx.homeroomClassName || '';
        if (className) {
          headerInfo.textContent = `CLASS: ${className} - SEMESTER: ${globalSemesterFilter.value}`;
        }
      }
    }

    if (globalSemesterFilter && globalSemesterFilter.value !== '') {
      if (hiddenSemester) hiddenSemester.value = globalSemesterFilter.value;
    } else {
      if (hiddenSemester) hiddenSemester.value = '';
      if (headerInfo) headerInfo.textContent = '';
    }
  }

  // Function to toggle Define Tests card visibility
  function toggleDefineTestsCard() {
    const defineTestsCard = document.getElementById('defineTestsCard');
    const createTestsBtn = document.getElementById('createTestsBtn');

    if (!defineTestsCard || !createTestsBtn) return;

    const translations = getContext().translations || {};

    if (defineTestsCard.style.display === 'none' || defineTestsCard.style.display === '') {
      defineTestsCard.style.display = 'block';
      createTestsBtn.innerHTML = '<i class="fas fa-eye-slash me-1"></i>' + (translations.hideForm || 'Hide Form');
    } else {
      defineTestsCard.style.display = 'none';
      createTestsBtn.innerHTML = '<i class="fas fa-plus me-1"></i>' + (translations.createTests || 'Create Tests');
      resetForm();
    }
  }

  // Callback function for when global filters change (called by base.html)
  function onGlobalFiltersChanged() {
    filterTests();
    checkCreateTestsButtonState();
  }

  // Initialize page when DOM is loaded
  function initCreateTestsPage() {
    // Wait a moment for global filters (populated by base.html), then proceed
    setTimeout(function () {
      if (typeof window.onGlobalFiltersChanged === 'function') {
        window.onGlobalFiltersChanged();
      }
    }, 200);

    filterTests();
    checkCreateTestsButtonState();
    calculateTotals();

    const subjectFilter = document.getElementById('filter_subject');
    if (subjectFilter) {
      subjectFilter.addEventListener('change', function () {
        filterTests();
      });
    }

    updateDefineTestsDisplay();
    checkCreateTestsButtonState();

    const createTestsBtn = document.getElementById('createTestsBtn');
    if (createTestsBtn) {
      createTestsBtn.addEventListener('click', toggleDefineTestsCard);
    }

    const defineTestsForm = document.querySelector('#defineTestsCard form');
    if (defineTestsForm) {
      defineTestsForm.addEventListener('submit', function () {
        updateDefineTestsDisplay();
      });
    }

    const testDate = document.getElementById('test_date');
    if (testDate) {
      const today = new Date().toISOString().split('T')[0];
      testDate.value = today;
    }

    const teacherType = getTeacherType();

    const filterSemesterSelect = document.getElementById('filter_semester');
    if (filterSemesterSelect) {
      filterSemesterSelect.value = '';
    }

    if (teacherType === 'specialist') {
      const filterGradeSelect = document.getElementById('filter_grade');
      const filterClassSelect = document.getElementById('filter_class');

      if (filterGradeSelect) {
        filterGradeSelect.value = '';
      }
      if (filterClassSelect) {
        filterClassSelect.value = '';
      }

      updateFilterClassOptions();
    } else {
      const filterSubjectSelect = document.getElementById('filter_subject');
      if (filterSubjectSelect) {
        filterSubjectSelect.value = '';
      }
    }

    if (teacherType === 'specialist') {
      const lastTestGrade = getContext().lastTestGrade || null;
      const lastTestClassName = getContext().lastTestClassName || null;

      if (lastTestGrade) {
        const gradeSelect = document.getElementById('grade');
        if (gradeSelect) {
          gradeSelect.value = lastTestGrade;
        }
        updateClassOptions();
      }

      if (lastTestClassName) {
        const classSelect = document.getElementById('class_name');
        if (classSelect) {
          classSelect.value = lastTestClassName;
        }
      }
    }

    filterTests();
  }

  // Expose functions used by inline HTML handlers
  window.editTest = editTest;
  window.confirmDeleteTest = confirmDeleteTest;

  // Called by base.html when global dropdowns are populated/changed
  window.onGlobalFiltersChanged = onGlobalFiltersChanged;

  // Optional debug / manual calls
  window._createTests = {
    filterTests,
    checkCreateTestsButtonState,
    calculateTotals,
    updateDefineTestsDisplay,
    toggleDefineTestsCard,
    onGlobalFiltersChanged,
    updateClassOptions,
    updateGradeFromClassForm,
    updateGradeFromClass,
    updateFilterClassOptions,
  };

  document.addEventListener('DOMContentLoaded', initCreateTestsPage);
})();
